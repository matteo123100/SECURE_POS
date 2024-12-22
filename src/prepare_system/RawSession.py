import pandas as pd
import numpy as np
import ipaddress


class RawSession():
    def __init__(self, UUID, myDB):
        # Recupera i dati dalle diverse tabelle nel database usando l'UUID
        query = "SELECT UUID, LABEL FROM labels WHERE UUID=?"
        self.Rlabels = myDB.read_sql(query, [UUID])

        query = "SELECT UUID, targetIP, destIP FROM networkMonitor WHERE UUID=?"
        self.Rnetwork = myDB.read_sql(query, [UUID])

        query = "SELECT UUID, latitude, longitude FROM localizationSys WHERE UUID=?"
        self.Rlocalization = myDB.read_sql(query, [UUID])

        query = """
            SELECT UUID, ts1, ts2, ts3, ts4, ts5, ts6, ts7, ts8, ts9, ts10, 
                   am1, am2, am3, am4, am5, am6, am7, am8, am9, am10 
            FROM transactionCloud WHERE UUID=?
        """
        self.Rtransaction = myDB.read_sql(query, [UUID])

    def mark_missing_samples(self):
        # Stampa la percentuale di valori mancanti in tutti i record
        records = [self.Rlabels, self.Rnetwork, self.Rtransaction, self.Rlocalization]

        count_null = 0  # Numero totale di valori nulli
        count_elem = 0  # Numero totale di elementi

        for record in records:
            count_elem += record.size
            count_null += record.isna().sum().sum()

        # Calcolo della percentuale di valori mancanti
        missing_ratio = count_null / count_elem if count_elem > 0 else 0
        print(f"[INFO] Percentuale valori mancanti: {missing_ratio * 100:.2f}%")
        return missing_ratio
    def check_nan(self):
        if self.Rlabels.isnull().values.any() or \
           self.Rtransaction.isnull().values.any() or \
           self.Rnetwork.isnull().values.any() or  \
           self.Rlocalization.isnull().values.any():
            return True
    def correct_missing_samples(self):
        # Configura Pandas per mostrare tutte le colonne senza troncamenti
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)

        # Corregge i valori mancanti nelle serie temporali dei dati transazionali
        self.Rtransaction = self.Rtransaction.applymap(lambda x: np.nan if x is None else x)

        # Interpolazione dei dati mancanti nelle colonne `ts` (serie temporali)
        ts = self.Rtransaction[['ts1', 'ts2', 'ts3', 'ts4', 'ts5', 'ts6', 'ts7', 'ts8', 'ts9', 'ts10']]
        ts = ts.interpolate(axis=1)
        self.Rtransaction[['ts1', 'ts2', 'ts3', 'ts4', 'ts5', 'ts6', 'ts7', 'ts8', 'ts9', 'ts10']] = ts

        # Interpolazione dei dati mancanti nelle colonne `am` (serie temporali)
        am = self.Rtransaction[['am1', 'am2', 'am3', 'am4', 'am5', 'am6', 'am7', 'am8', 'am9', 'am10']]
        am = am.interpolate(axis=1)
        self.Rtransaction[['am1', 'am2', 'am3', 'am4', 'am5', 'am6', 'am7', 'am8', 'am9', 'am10']] = am

        # Corregge i valori mancanti nelle informazioni di rete
        self.Rnetwork = self.Rnetwork.applymap(lambda x: np.nan if x is None else x)
        if self.Rnetwork.shape[0] > 1:
            # Usa il valore più recente per riempire i valori mancanti
            if pd.isna(self.Rnetwork['targetIP'].iloc[0]):
                self.Rnetwork['targetIP'].iloc[0] = self.Rnetwork['targetIP'].iloc[-1]

            if pd.isna(self.Rnetwork['destIP'].iloc[0]):
                self.Rnetwork['destIP'].iloc[0] = self.Rnetwork['destIP'].iloc[-1]

            self.Rnetwork[['targetIP', 'destIP']] = self.Rnetwork[['targetIP', 'destIP']].fillna(method='ffill')

        # Corregge i valori mancanti nelle coordinate di localizzazione
        self.Rlocalization = self.Rlocalization.applymap(lambda x: np.nan if x is None else x)
        if self.Rlocalization.shape[0] > 1:
            # Usa il valore più recente per riempire i valori mancanti
            if pd.isna(self.Rlocalization['latitude'].iloc[0]):
                self.Rlocalization['latitude'].iloc[0] = self.Rlocalization['latitude'].iloc[-1]

            if pd.isna(self.Rlocalization['longitude'].iloc[0]):
                self.Rlocalization['longitude'].iloc[0] = self.Rlocalization['longitude'].iloc[-1]

            self.Rlocalization[['latitude', 'longitude']] = self.Rlocalization[['latitude', 'longitude']].fillna(
                method='ffill')

    def correct_outliers(self):
        # Corregge eventuali valori fuori dal range accettabile nelle coordinate di localizzazione
        max_latitude = 90
        min_latitude = -90
        max_long = 180
        min_long = -180

        self.Rlocalization.loc[self.Rlocalization['latitude'] > max_latitude, 'latitude'] = max_latitude
        self.Rlocalization.loc[self.Rlocalization['latitude'] < min_latitude, 'latitude'] = min_latitude
        self.Rlocalization.loc[self.Rlocalization['longitude'] > max_long, 'longitude'] = max_long
        self.Rlocalization.loc[self.Rlocalization['longitude'] < min_long, 'longitude'] = min_long

    def extract_features(self):
        # Estrae caratteristiche dai dati per analisi successive

        # Calcola le mediane di latitudine e longitudine
        median_latitude = self.Rlocalization['latitude'].median()
        median_longitude = self.Rlocalization['longitude'].median()

        # Calcola le mediane per IP di destinazione e target convertiti in numeri interi
        self.Rnetwork['target'] = self.Rnetwork['targetIP'].apply(lambda x: int(ipaddress.ip_address(x)))
        median_targetIP = self.Rnetwork['target'].median()
        median_targetIP = str(ipaddress.ip_address(int(median_targetIP)))

        self.Rnetwork['dest'] = self.Rnetwork['destIP'].apply(lambda x: int(ipaddress.ip_address(x)))
        median_destIP = self.Rnetwork['dest'].median()
        median_destIP = str(ipaddress.ip_address(int(median_destIP)))

        # Calcola le differenze assolute medie per le serie temporali `ts` e `am`
        self.Rtransaction['mean_abs_diff_ts'] = self.Rtransaction.filter(like='ts').diff(axis=1).abs().mean(axis=1)
        self.Rtransaction['mean_abs_diff_am'] = self.Rtransaction.filter(like='am').diff(axis=1).abs().mean(axis=1)

        mean_abs_diff_ts = self.Rtransaction['mean_abs_diff_ts'].mean()
        mean_abs_diff_am = self.Rtransaction['mean_abs_diff_am'].mean()

        # Ottiene l'etichetta + presente
        label = self.Rlabels['LABEL'].mode()[0]

        # Ritorna le caratteristiche estratte
        features = [mean_abs_diff_ts, mean_abs_diff_am, median_longitude, median_latitude, median_targetIP,
                    median_destIP, label]
        return features
