def lin_mini(vector, sample):
    import numpy as np

    sz_sample = np.shape(sample)
    sz_vector = np.shape(vector)

    if sz_vector[0] == sz_sample[0]:
        cas = 2
    if sz_vector[0] == sz_sample[1]:
        cas = 1

    #
    # vecteur de N elements
    # sample : matrice N*M, chacune des M colonnes est ajustee en amplitude
    # pour minimiser le chi2 par rapport au vecteur d'entree
    # output : vecteur de M de long qui donne les amplitudes de chaque colonne
    #
    # returns NaN values as amplitudes if the sample vectors lead to an
    # auto-correlation matrix that
    # cannot be inverted (i.e., that are full of zeros or are not linearly
    # independent)
    #
    vector = np.asarray(vector)
    sample = np.asarray(sample)
    sz_sample = np.shape(sample)

    # noinspection PyUnboundLocalVariable
    if cas == 1:
        #
        mm = np.zeros([sz_sample[0], sz_sample[0]])
        #
        v = np.zeros(sz_sample[0])

        for i in range(sz_sample[0]):
            for j in range(i, sz_sample[0]):
                mm[i, j] = np.sum(sample[i, :] * sample[j, :])
                mm[j, i] = mm[i, j]
            v[i] = np.sum(vector * sample[i, :])
        #
        if np.linalg.det(mm) == 0:
            amps = np.zeros(sz_sample[0]) + np.nan
            recon = np.zeros_like(v)
            return amps, recon

        amps = np.matmul(np.linalg.inv(mm), v)
        #
        recon = np.zeros(sz_sample[1])
        #
        for i in range(sz_sample[0]):
            recon += amps[i] * sample[i, :]
        #
        return amps, recon

    if cas == 2:
        # print('cas = 2')
        # print(sz_sample[1])
        mm = np.zeros([sz_sample[1], sz_sample[1]])
        v = np.zeros(sz_sample[1])

        for i in range(sz_sample[1]):
            for j in range(i, sz_sample[1]):
                mm[i, j] = np.sum(sample[:, i] * sample[:, j])
                mm[j, i] = mm[i, j]
            v[i] = np.sum(vector * sample[:, i])

        if np.linalg.det(mm) == 0:
            amps = np.zeros(sz_sample[1]) + np.nan
            recon = np.zeros_like(v)
            return amps, recon

        amps = np.matmul(np.linalg.inv(mm), v)

        recon = np.zeros(sz_sample[0])

        for i in range(sz_sample[1]):
            recon += amps[i] * sample[:, i]

        return amps, recon
