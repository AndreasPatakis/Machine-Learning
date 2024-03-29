import numpy as np
import random as rand

class Neural_Network:
    def __init__(self,X,Layers,a):
        self.X = X
        self.Layers = Layers
        self.Learning_Rate = a
        self.Weights = []
        self.Biases = np.array
        self.H = []
        self.d_Hout_Total = []
        self.Evaluation = 0
        self.d_Weights = []
        self.d_Biases = []
        self.__do_prework()

    def __activation_net(self, W,X,b):
        return W@X+b

    def __activation_out(self,net):
        return self.__sigmoid(net)

    def __sigmoid(self,x):
        return 1/(1 + np.exp(-x))

    def __d_sigmoid(self,z):
        f = 1/(1+np.exp(-z))
        r = f * (1 - f)
        return r

    #Calculates the derivative dErrorTotal/dh(L-1)out for the node curr_node
    def __d_SSR(self,observed,curr_node):
        sum = 0
        for node in range(self.Layers[-1]):
            predicted = self.H[-1][node][1]
            z = self.H[-1][node][0]
            w = self.Weights[-1][curr_node][node]
            sum += -2*(observed[node]-predicted)*self.__d_sigmoid(z)*w
        return sum

    #Calculates the derivate of every node(h_out)
    #Practically this means that we calculate the total "contribution"
    #of each node to the final outcome(SSR)
    def __d_hout(self,curr_l,curr_node):
        next_layer = curr_l + 1
        next_layer_nodes = self.Layers[next_layer]
        d_h_out = 0
        for node in range(next_layer_nodes):
            d_h_out_next_node = self.d_Hout_Total[next_layer][node]
            d_act_next_node = self.__d_sigmoid(self.H[next_layer][node][0])
            d_w_next_node = self.Weights[next_layer][curr_node][node]
            d_next_node = d_h_out_next_node * d_act_next_node * d_w_next_node
            d_h_out += d_next_node
        return d_h_out




    #Methods of parent class
    def __do_prework(self):
        num_of_layers = len(self.Layers)
        weights = [[]for x in range(num_of_layers)]
        biases = [[]for x in range(num_of_layers)]
        hout = [[]for x in range(num_of_layers)]
        for layer,nodes in enumerate(self.Layers):
            b = []
            if(layer == 0): #The first layer so we have to take as inputs the Xi's
                w = [[]for x in range(nodes)]
                features = self.X
                for node in range(nodes):
                    b.append(0.0)
                    for inputs in range(features):
                        w[node].append(rand.uniform(0.0,1.0))
            else:
                w = [[]for x in range(nodes)]
                for node in range(nodes):
                    b.append(0.0)
                    for inputs in range(self.Layers[layer-1]):
                        w[node].append(rand.uniform(0.0,1.0))
            biases[layer] = np.array(b)
            #d_Hout_Total has the same matrix structure as biases, so we just copy that.
            #THERE IS NO RELATION BETWEEN THE TWO.
            hout[layer] = np.array(b)
            w_i = np.array(w).T
            weights[layer] = w_i
        self.Weights = weights
        self.Biases = biases
        self.d_Hout_Total = hout
        self.H = [[]for x in range(num_of_layers)]

    def __forward_feed(self,set):
        for layer,nodes in enumerate(self.Layers):
            h = []
            if(layer == 0): #In this case we have to take Xi's as inputs
                X = set
            else:
                X = self.H[layer-1][:,1]    #0 for the net value and 1 for the out value
            for node in range(nodes):
                W = self.Weights[layer][:,node]
                b = self.Biases[layer][node]
                net = self.__activation_net(W,X,b)
                out = self.__activation_out(net)
                h.append([net,out])
            self.H[layer] = np.array(h)


    def __backprop_Last(self,observed): #Observed is a vector of the real outputs for current set
        layers = len(self.Layers)
        x = self.Layers[-2]
        y = self.Layers[-1]
        w_reverse = np.zeros(shape=(x,y))
        b_reverse = np.zeros(y)
        if(len(self.d_Weights) < 1):
            self.d_Weights.append(w_reverse)
            self.d_Biases.append(b_reverse)
        for curr_node in range(self.Layers[-1]):    #For each node of the last layer
            w_temp = []
            predicted_curr = self.H[-1][curr_node][1]
            z = self.H[-1][curr_node][0]
            d_h_out_last = -2*(observed[curr_node]-predicted_curr)
            self.d_Hout_Total[layers-1][curr_node] = d_h_out_last
            b = d_h_out_last * self.__d_sigmoid(z)
            for prev_node in range(self.Layers[-2]):
                predicted_prev = self.H[-2][prev_node][1]
                derivate = d_h_out_last * self.__d_sigmoid(z)*predicted_prev
                w_temp.append(derivate)
            w_reverse[:,curr_node] += np.array(w_temp).T
            b_reverse[curr_node] += b
        self.d_Weights[0]+=w_reverse
        self.d_Biases[0]+=b_reverse

    def __backprop_Previous(self,set):
        layers = len(self.Layers)-1
        for layer in range(layers-1,-1,-1):
            curr_nodes = self.Layers[layer]
            if(layer == 0):
                prev_nodes = self.X
            else:
                prev_nodes = self.Layers[layer-1]
            w_reverse = np.zeros(shape=(prev_nodes,curr_nodes))
            b_reverse = np.zeros(curr_nodes)
            if(len(self.d_Weights) < layers+1):
                self.d_Weights.append(w_reverse)
                self.d_Biases.append(b_reverse)
            for node in range(self.Layers[layer]):
                w_temp = []
                d_h_out = self.__d_hout(layer,node)
                self.d_Hout_Total[layer][node] = d_h_out
                z = self.__sigmoid(self.H[layer][node][0])
                b = d_h_out*z
                if(layer == 0):
                    for input in set:
                        derivative = d_h_out*z*input
                        w_temp.append(derivative)
                else:
                    for input in self.H[layer-1]:
                        derivative = d_h_out*z*input[1]
                        w_temp.append(derivative)
                w_reverse[:,node] += np.array(w_temp).T
                b_reverse[node] += b
                self.d_Weights[layers-layer]+=w_reverse
                self.d_Biases[layers-layer]+=b_reverse



    #X is a matrix, each row represents each input and each column the current value of a set
    #Y is a matrix containing the observed results for each set of inputs
    def __GradientDescent(self,X,Y,batch):
        total_sets = len(X[0])
        total_batches = int(total_sets/batch)
        for j in range(total_batches):
            for i in range(j*batch,(j+1)*batch):
                set = X[:,i]
                observed = Y[:,i]
                self.__forward_feed(set)
                self.__backprop_Last(observed)
                self.__backprop_Previous(set)
            self.d_Weights.reverse()                     #d_Weights contains the Sum of the derivatives of the weights. Reverse(because [0] == last layer weights)
            self.d_Biases.reverse()                      #Same thing but for the biases
            layers = len(self.Layers)
            for layer in range(layers):
                inputs = len(self.Weights[layer])
                #Calculating new weights
                for feature in range(inputs):
                    nodes =  len(self.Weights[layer][feature])
                    for node in range(nodes):
                        old_weight = self.Weights[layer][feature][node]
                        derivative = self.d_Weights[layer][feature][node]
                        step_size = derivative*self.Learning_Rate
                        new_weight = old_weight - step_size
                        self.Weights[layer][feature][node] = new_weight
                #Calculating new biases
                for node in range(len(self.Biases[layer])):
                    old_bias = self.Biases[layer][node]
                    derivative = self.d_Biases[layer][node]
                    step_size = derivative*self.Learning_Rate
                    new_bias = old_bias - step_size
                    self.Biases[layer][node] = new_bias
            #print(self.d_Weights)
            self.d_Weights = []
            self.d_Biases = []

    def __evaluate(self,set,observed):
        self.__forward_feed(set)
        prediction = []
        result = observed.tolist()
        last_layer = self.H[-1]
        #print(last_layer)
        for node in last_layer:
            prediction.append(node[1])               #0 for net value(before normalization(sigmoid)), 1 is for output value
        pos_prediction = prediction.index(max(prediction))
        pos_result = result.index(max(result))
        if(pos_prediction == pos_result):
            return 1
        else:
            return 0

    def feed_forward_result(self,set):
        self.__forward_feed(set)
        nn_result = self.H[-1].tolist()
        nn_result_sig=[]
        for node in nn_result:
            nn_result_sig.append(node[1])
        prediction = [0]*len(nn_result_sig)
        prediction[nn_result_sig.index(max(nn_result_sig))] = 1
        return prediction


    def get_Eval(self):
        return self.Evaluation

    def train(self,X,Y,epochs,batch):
        X = np.array(X).T
        Y = np.array(Y).T
        for epoch in range(epochs):
            self.__GradientDescent(X,Y,batch)
            print("\tEpoch: ",epoch+1,"/",epochs," completed.")

    def test(self,X,Y):
        X = np.array(X).T
        Y = np.array(Y).T
        total_sets = len(X[0])
        correct = 0
        for i in range(total_sets):               #For each pair of data(one set of inputs, one set of outputs)
            set = X[:,i]                          #Pair of inputs
            observed = Y[:,i]
            correct += self.__evaluate(set,observed)
        score = (correct/total_sets)*100
        self.Evaluation = score
