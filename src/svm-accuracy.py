import matplotlib
from sklearn import svm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


class SVM:

    def __init__(self):
        self.basic_s1_clf = self.train("basic", "s1")
        self.basic_s11_clf = self.train("basic", "s11")
        self.basic_s12_clf = self.train("basic", "s12")
        self.large_s1_clf = self.train("large", "s1")
        self.large_s11_clf = self.train("large", "s11")
        self.large_s12_clf = self.train("large", "s12")
        self.large_s13_clf = self.train("large", "s13")
        self.large_s14_clf = self.train("large", "s14")
        self.large_s15_clf = self.train("large", "s15")

    @staticmethod
    def train(topology, switch):
        normal_file = topology + "-label0-features-" + switch
        attack_file = topology + "-label1-features-" + switch
        with open("../data/" + normal_file, "r") as nf:
            normal_features = nf.read().split("\n")[:-1]
            normal_features = normal_features[:int(len(normal_features) * 0.8)]
        with open("../data/" + attack_file, "r") as nf:
            attack_features = nf.read().split("\n")[:-1]
            attack_features = attack_features[:int(len(attack_features) * 0.8)]

        labels = [0] * len(normal_features) + [1] * len(attack_features)
        train_data = []
        for entry in normal_features:
            features = entry.split(',')
            features = [float(i) for i in features]
            train_data.append(features)

        for entry in attack_features:
            features = entry.split(',')
            features = [float(i) for i in features]
            train_data.append(features)

        clf = svm.SVC()
        clf.fit(train_data, labels)

        return clf

    def predict(self, topology, switch, features):
        features = features.split(",")
        test_data = [[float(i) for i in features]]

        prediction = None
        if topology == "basic":
            if switch == "s1":
                prediction = self.basic_s1_clf.predict(test_data)[0]
            if switch == "s11":
                prediction = self.basic_s11_clf.predict(test_data)[0]
            if switch == "s12":
                prediction = self.basic_s12_clf.predict(test_data)[0]

        if topology == "large":
            if switch == "s1":
                prediction = self.large_s1_clf.predict(test_data)[0]
            if switch == "s11":
                prediction = self.large_s11_clf.predict(test_data)[0]
            if switch == "s12":
                prediction = self.large_s12_clf.predict(test_data)[0]
            if switch == "s13":
                prediction = self.large_s13_clf.predict(test_data)[0]
            if switch == "s14":
                prediction = self.large_s14_clf.predict(test_data)[0]
            if switch == "s15":
                prediction = self.large_s15_clf.predict(test_data)[0]

        return prediction, test_data[0][0], test_data[0][1], test_data[0][2], test_data[0][3], test_data[0][4], \
               test_data[0][5], test_data[0][6], test_data[0][7], test_data[0][8]


def find_accuracy(model, topo, switch):
    normal_file = "../data/" + topo + "-label0-features-" + switch
    with open(normal_file, "r") as nf:
        normal_features = nf.read().split("\n")[:-1]
        normal_features = normal_features[int(len(normal_features) * 0.8):]

    attack_file = "../data/" + topo + "-label1-features-" + switch
    with open(attack_file, "r") as nf:
        attack_features = nf.read().split("\n")[:-1]
        attack_features = attack_features[int(len(attack_features) * 0.8):]

    labels = [0] * len(normal_features) + [1] * len(attack_features)

    test_data = normal_features + attack_features
    print(test_data)

    mistakes = 0
    predictions = []
    APfs = []
    MPfs = []
    ABfs = []
    MBfs = []
    ADfs = []
    MDfs = []
    PPfs = []
    GSfs = []
    GDPs = []
    x = []
    for i in range(len(test_data)):
        prediction, apf, mpf, abf, mbf, adf, mdf, ppf, gsf, gdp = model.predict(topo, switch, test_data[i])
        predictions.append(prediction)
        APfs.append(apf)
        MPfs.append(mpf)
        ABfs.append(abf)
        MBfs.append(mbf)
        ADfs.append(mdf)
        MDfs.append(mdf)
        PPfs.append(ppf)
        GSfs.append(gsf)
        GDPs.append(gdp)
        x.append(i + 1)
        # print prediction
        # print labels[i]
        if prediction != labels[i]:
            mistakes += 1

    fig, axs = plt.subplots(3, 3)
    cmap = matplotlib.cm.get_cmap('Dark2')
    custom_lines = [Line2D([0], [0], color=cmap(0.), lw=4),
                    Line2D([0], [0], color=cmap(1.), lw=4)]

    axs[0, 0].scatter(x, APfs, c=labels, alpha=0.4, s=50, cmap='Dark2')
    # axs[0, 0].set_xlabel('time')
    axs[0, 0].set_ylabel('APf')
    axs[1, 0].scatter(x, MPfs, c=labels, alpha=0.4, s=50, cmap='Dark2')
    # axs[1, 0].set_xlabel('time')
    axs[1, 0].set_ylabel('MPf')
    axs[2, 0].scatter(x, ABfs, c=labels, alpha=0.4, s=50, cmap='Dark2')
    # axs[2, 0].set_xlabel('time')
    axs[2, 0].set_ylabel('ABf')
    axs[0, 1].scatter(x, MBfs, c=labels, alpha=0.4, s=50, cmap='Dark2')
    # axs[0, 1].set_xlabel('time')
    axs[0, 1].set_ylabel('MBf')
    axs[1, 1].scatter(x, ADfs, c=labels, alpha=0.4, s=50, cmap='Dark2')
    # axs[1, 1].set_xlabel('time')
    axs[1, 1].set_ylabel('ADf')
    axs[2, 1].scatter(x, MDfs, c=labels, alpha=0.4, s=50, cmap='Dark2')
    # axs[2, 1].set_xlabel('time')
    axs[2, 1].set_ylabel('MDf')
    axs[0, 2].scatter(x, PPfs, c=labels, alpha=0.4, s=50, cmap='Dark2')
    # axs[0, 2].set_xlabel('time')
    axs[0, 2].set_ylabel('PPf')
    # axs[0, 2].legend(custom_lines, ['normal traffic', 'DDoS attack'])
    axs[1, 2].scatter(x, GSfs, c=labels, alpha=0.4, s=50, cmap='Dark2')
    # axs[1, 2].set_xlabel('time')
    axs[1, 2].set_ylabel('GSf')
    axs[2, 2].scatter(x, GDPs, c=labels, alpha=0.4, s=50, cmap='Dark2')
    # axs[2, 2].set_xlabel('time')
    axs[2, 2].set_ylabel('GDP')

    fig.show()

    print mistakes
    print len(labels)
    print("Accuracy of " + switch + " in " + topo + " topology: " + str((1 - mistakes * 1.0 / len(labels)) * 100))
    return x, predictions, labels


model = SVM()
x1, pred1, label1 = find_accuracy(model, "basic", "s1")
# x2, pred2, label2 = find_accuracy(model, "basic", "s11")
# x3, pred3, label3 = find_accuracy(model, "basic", "s12")
# fig, axs = plt.subplots(3,1)
# cmap = matplotlib.cm.get_cmap('Spectral')
# custom_lines = [Line2D([0], [0], color=cmap(0.), lw=4),
#                 Line2D([0], [0], color=cmap(1.), lw=4)]
# axs[0].scatter(x1, pred1, c=label1, alpha=0.4, s=50, cmap='Spectral')
# axs[0].set_title('s1')
# axs[0].set_xlabel('time')
# axs[0].set_ylabel('prediction')
# axs[0].legend(custom_lines, ['normal traffic', 'DDoS attack'])
# axs[1].scatter(x2, pred2, c=label2, alpha=0.4, s=50, cmap='Spectral')
# axs[1].set_title('s11')
# axs[1].set_xlabel('time')
# axs[1].set_ylabel('prediction')
# axs[2].scatter(x3, pred3, c=label3, alpha=0.4, s=50, cmap='Spectral')
# axs[2].set_title('s12')
# axs[2].set_xlabel('time')
# axs[2].set_ylabel('prediction')

# fig.show()
#
#
# x1, pred1, label1 = find_accuracy(model, "large", "s1")
# x2, pred2, label2 = find_accuracy(model, "large", "s11")
# x3, pred3, label3 = find_accuracy(model, "large", "s12")
# x4, pred4, label4 = find_accuracy(model, "large", "s13")
# x5, pred5, label5 = find_accuracy(model, "large", "s14")
# x6, pred6, label6 = find_accuracy(model, "large", "s15")
#
# fig, axs = plt.subplots(3,2)
# cmap = matplotlib.cm.get_cmap('Spectral')
# custom_lines = [Line2D([0], [0], color=cmap(0.), lw=4),
#                 Line2D([0], [0], color=cmap(1.), lw=4)]
# axs[0, 0].scatter(x1, pred1, c=label1, alpha=0.4, s=50, cmap='Spectral')
# axs[0, 0].set_title('s1')
# axs[0, 0].set_xlabel('time')
# axs[0, 0].set_ylabel('prediction')
# axs[1, 0].scatter(x2, pred2, c=label2, alpha=0.4, s=50, cmap='Spectral')
# axs[1, 0].set_title('s11')
# axs[1, 0].set_xlabel('time')
# axs[1, 0].set_ylabel('prediction')
# axs[2, 0].scatter(x3, pred3, c=label3, alpha=0.4, s=50, cmap='Spectral')
# axs[2, 0].set_title('s12')
# axs[2, 0].set_xlabel('time')
# axs[2, 0].set_ylabel('prediction')
#
# axs[0, 1].scatter(x4, pred4, c=label4, alpha=0.4, s=50, cmap='Spectral')
# axs[0, 1].set_title('s13')
# axs[0, 1].set_xlabel('time')
# axs[0, 1].set_ylabel('prediction')
# axs[0, 1].legend(custom_lines, ['normal traffic', 'DDoS attack'])
# axs[1, 1].scatter(x5, pred5, c=label5, alpha=0.4, s=50, cmap='Spectral')
# axs[1, 1].set_title('s14')
# axs[1, 1].set_xlabel('time')
# axs[1, 1].set_ylabel('prediction')
# axs[2, 1].scatter(x6, pred6, c=label6, alpha=0.4, s=50, cmap='Spectral')
# axs[2, 1].set_title('s15')
# axs[2, 1].set_xlabel('time')
# axs[2, 1].set_ylabel('prediction')
#
# fig.show()
