import numpy as np
import math

# The method is called PCA but they never mention standardizing the data. That
# is why I am not scaling or standardizing the data.

# This method has a problem with this dynamic matrix. If we fix it static it
# wont be effective for mitigation, but If we let it grow then in the longer
# term we wont be able to store the whole matrix.

class PCA:

    def __init__(self):
        self.X = None
        self.od_pairs = {}  # This dict is for storing the index of each pair in the matrix
        self.n_pairs = 0

    def compute_residual(self, flows):
        if len(flows) == 0: return 0
        #print('----flows---')
        #print(flows)

        if self.od_pairs:
            packet_list = [0 for i in range(len(self.od_pairs))]
        else:
            packet_list = []

        for flow in flows:
            src = flow['eth_src']
            dst = flow['eth_dst']
            packets = flow['packets']
            od_key = tuple(sorted((src, dst)))

            if od_key not in self.od_pairs:
                self.od_pairs[od_key] = self.n_pairs
                packet_list.append(packets)  # this pair is new.
                self.n_pairs += 1
            else:
                packet_list[self.od_pairs[od_key]] = packets  # insert the packets in the corresponding index.

        x = np.array(packet_list)   # Convert the list into array for building the matrix.
        # print('----x---')
        # print(x)

        if self.X is not None:
            if x.shape[0] > self.X.shape[1]:  # If we got new pairs.
                pad = x.shape[0] - self.X.shape[1]  # calculate how many new pairs.
                aux = np.zeros((self.X.shape[0], pad))
                self.X = np.hstack((self.X, aux))  # Fill the previous ones with zeros

        else:
            self.X = x.reshape((1,-1))
        # print('----Matrix---')
        # print(self.X)

        if self.X.shape[0] > self.X.shape[1]:
            # Compute the SVD
            u, s, v = np.linalg.svd(self.X, full_matrices=False)
            I = np.eye(x.shape[0])
            C_tilde = I - np.matmul(u.transpose(),u)
            x_tilde = np.matmul(C_tilde,x.reshape((-1,1)))
            # print('----x_tilde---')
            # print(x_tilde)
            residual = np.linalg.norm(x_tilde)
        else:
            residual = 0

        #increase the size of the matrix with the new flow.

        self.X = np.vstack((self.X, x))

        if residual == 0: return 0
        return math.log(residual)


