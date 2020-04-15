import numpy as np

#untested class
# the matrix X is dynamic, that is why I am doing all this,
# maybe we can try with a matrix with a bunch of zeros,
# but that may not make sense.

class calculate_PCA:

    def __init__(self):
        self.X = None
        pass

    def build_matrix(self,flows):
        n_pairs = 0
        od_pairs = {}  #This dict is for storing the index of each pair in the matrix

        if od_pairs:
            packet_list = [0 for i in range(len(od_pairs))]
        else:
            packet_list = []

        for flow in flows:
            print flow
            src = flow['eth_src']
            dst = flow['eth_dst']
            packets = flow['packets']
            od_key = tuple(sorted((src,dst)))

            if od_key not in od_pairs:
                od_pairs[od_key] = n_pairs
                packet_list.append(packets)  #this pair is new.
                n_pairs += 1
            else:
                packet_list[od_pairs[od_key]] = packets #insert the packets in the corresponding index.

        x = np.array(packet_list) # Convert the list into array for building the matrix.

        if self.X:
            if x.shape[0] > self.X.shape[1]:  #If we got new pairs.
                pad = x.shape[0] - self.X.shape[1]  # calculate how many new pairs.
                aux = np.zeros((self.X.shape[0],pad))
                self.X = np.hstack((self.X,aux))   # Fill the previous ones with zeros

            self.X = np.vstack(self.X,x)
        else:
            self.X = x

    def compute (self, x ):

        # Compute the SVD
        u, s, v = np.linalg.svd(self.X, full_matrices=False)
        I = np.eye(x.shape[0])
        C_tilde = I - np.matmul(u.transpose(),u)
        x_tilde = np.matmul(C_tilde,x.reshape((-1,1)))
        residual = np.linalg.norm(x_tilde)

        #The method is called PCA but they never mention standardizing the data. That
        # is why I am not scaling or standardizing the data.

        #This method has a problem with this dynamic matrix. If we fix it static it
        # wont be effective for mitigation, but If we let it grow then in the longer
        # term we wont be able to store the whole matrix.

        return residual


