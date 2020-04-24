from sklearn import svm


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

        return prediction


def find_accuracy(model, topo, switch):
    normal_file = "../data/test/test-" + topo + "-features-" + switch
    with open(normal_file, "r") as nf:
        normal_features = nf.read().split("\n")[:-1]
        # normal_features = normal_features[int(len(normal_features) * 0.2):]

    # attack_file = "../data/" + topo + "-label1-features-" + switch
    # with open(attack_file, "r") as nf:
    #     attack_features = nf.read().split("\n")[:-1]
    #     attack_features = attack_features[int(len(attack_features) * 0.8):]

    #labels = [0] * len(normal_features) + [1] * len(attack_features)
    labels = [0] * len(normal_features)

    #test_data = normal_features + attack_features
    test_data = normal_features

    mistakes = 0
    for i in range(len(test_data)):
        prediction = model.predict(topo, switch, test_data[i])
        # print prediction
        # print labels[i]
        if prediction != labels[i]:
            mistakes += 1
    # print mistakes
    # print len(labels)
    print("Accuracy of " + switch + " in " + topo + " topology: " + str((1 - mistakes * 1.0 / len(labels)) * 100))


model = SVM()
find_accuracy(model, "basic", "s1")
find_accuracy(model, "basic", "s11")
find_accuracy(model, "basic", "s12")
# find_accuracy(model, "large", "s1")
# find_accuracy(model, "large", "s11")
# find_accuracy(model, "large", "s12")
# find_accuracy(model, "large", "s13")
# find_accuracy(model, "large", "s14")
# find_accuracy(model, "large", "s15")
