"""
    LabelStoreController module, for label storing,
    and prompting report generation
"""
import threading
import pandas as pd

from evaluation_system.eval_ambient_flags_loader import DEBUGGING
from evaluation_system.label_store import LabelStore
from evaluation_system.evaluation_report_controller import EvaluationReportController


def prepare_label_dict(session_id, label_value, label_source):
    """
    Generate a Label object as dictionary, from given inputs
    :param session_id: label uuid
    :param label_value: label value (attack / normal)
    :param label_source: label source (classifier / expert)
    :return: returns the Label object as python dictionary
    """
    return {
        'session_id':
            session_id,
        'value':
            label_value,
        'source':
            label_source
    }


class LabelStoreController:
    """
        Class for managing Label storage calls,
        and, if conditions are met, requiring EvaluationReport generation
    """
    def __init__(self):
        """
        Need to keep count of labels from expert and classifier,
        will increase count upon label storing, based on label_source field value.
        """
        self.num_labels_from_expert = 0
        self.num_labels_from_classifier = 0
        self.enough_total_labels = False
        self.store = LabelStore()
        self.report = EvaluationReportController()
        self.db_semaphore = threading.Semaphore(1)
        # see : https://docs.python.org/3/library/threading.html
        # will call .release() with no arguments, since only 1 coin is available.

    def update_count_labels(self, label_source: str):
        """
            Update label count depending on label source
        :param label_source: shall be either <classifier> or <expert>
        :return:
        """
        if label_source == 'classifier':
            self.num_labels_from_classifier += 1
        elif label_source == 'expert':
            self.num_labels_from_expert += 1
        else:
            raise ValueError(f'Evaluation System working on unknown-origin label: '
                             f'src is {label_source}')

    def store_label(self,
                    min_labels_opinionated: int,
                    max_conflicting_labels_threshold: int,
                    max_consecutive_conflicting_labels_threshold: int,
                    label):
        """
            Method that acquires db semaphore (we are a thread after all),
            adds to db the label (if well formatted),
            and prompts report generation (and frees db)
            if requirements are met.
        :param min_labels_opinionated:
        :param max_conflicting_labels_threshold:
        :param max_consecutive_conflicting_labels_threshold:
        :param min_labels_opinionated:
        :param label:
        :return:
        """
        with self.db_semaphore:
            # receive labels as json, need to convert them to Label object.

            if DEBUGGING:
                print(f'label received id:{label["session_id"]}; '
                      f'value:{label["value"]}; '
                      f'source:{label["source"]}')

            # label = Label(session_id, label_value, label_source)
            label_dict = prepare_label_dict(label["session_id"], label["value"], label["source"])

            label_dataframe = pd.DataFrame(label_dict, index=[0],
                                           columns=["session_id", "value"])

            if label_dict["source"] == "classifier":
                self.store.ls_store_label_df(label_dataframe, 'classifierLabelTable')
                self.update_count_labels('classifier')
            elif label_dict["source"] == "expert":
                self.store.ls_store_label_df(label_dataframe, 'expertLabelTable')
                self.update_count_labels('expert')
            else:
                print(f'Non standard label arrived to store_label in EvalSys;\n'
                      f'label_src : {label_dict["source"]}')
                raise ValueError("Evaluation System working on unknown-origin label")

            # in order to there be enough opinionated,
            # there first need to be enough for each group,
            # this is a <NECESSARY> condition,
            # but obv it is <NOT SUFFICIENT>
            if not self.enough_total_labels:
                if self.num_labels_from_expert >= min_labels_opinionated and \
                        self.num_labels_from_classifier >= min_labels_opinionated:
                    self.enough_total_labels = True
            if self.enough_total_labels:
                print("Minimum condition for generate report is met")

                # load labels that have opinion from classifier AND expert,
                # matching on uuid
                load_matching_labels_query = \
                    "SELECT expertLT.session_id, " \
                    "expertLT.value as expertValue," \
                    "classifierLT.value as classifierValue " \
                    "FROM expertLabelTable AS expertLT " \
                    "INNER JOIN classifierLabelTable AS classifierLT " \
                    "ON expertLT.session_id = classifierLT.session_id"
                opinionated_labels = self.store.ls_select_labels(load_matching_labels_query, [])

                if DEBUGGING:
                    print(f'DBG, query opinionated labels returned : {opinionated_labels}')

                opinionated_session_id_list = opinionated_labels["session_id"].to_list()
                num_usable_labels = len(opinionated_session_id_list)

                # in order to complete the evaluation,
                # we need a minimum threshold of
                # labels with opinions from both classifier and expert
                if not num_usable_labels < min_labels_opinionated:
                    if DEBUGGING:
                        print(f'DBG, only {num_usable_labels} usable,'
                              f' need : {min_labels_opinionated}')
                if num_usable_labels >= min_labels_opinionated:
                    if DEBUGGING:
                        print(f'DBG, all record conditions have been met :{num_usable_labels};'
                              f' will generate the report')

                    query = "DELETE FROM expertLabelTable " + \
                            "WHERE session_id IN (" + \
                            str(opinionated_session_id_list)[1:-1] + ")"
                    self.store.ls_delete_labels(query, [])

                    query = "DELETE FROM classifierLabelTable " + \
                            "WHERE session_id IN (" + \
                            str(opinionated_session_id_list)[1:-1] + ")"
                    self.store.ls_delete_labels(query, [])

                    self.num_labels_from_expert -= min_labels_opinionated
                    self.num_labels_from_classifier -= min_labels_opinionated
                    # since all of these labels have been used,
                    # (but not all the labels that exist in our db),
                    # we clean this field, and it will be re-evaluated as a new label comes.
                    self.enough_total_labels = False

                    # all DB related operations for this thread are completed,
                    # release semaphore now.
                    self.db_semaphore.release()

                    # now we have all the labels with the correct requirements,
                    # we can start evaluating
                    print("Start EvaluationReport generation")
                    thread = threading.Thread(target=self.report.generate_report,
                                              args=(min_labels_opinionated,
                                                    max_conflicting_labels_threshold,
                                                    max_consecutive_conflicting_labels_threshold,
                                                    opinionated_labels))
                    thread.start()
