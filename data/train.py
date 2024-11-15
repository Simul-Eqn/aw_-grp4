# train 
import numpy as np 
import torch 

from model import Model 
from torch_model import TorchModel 
from mlrm import MLRM 
from dtree import DecisionTree 

from dataloader import load_data 
from datagen import data_generator 

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu') 


import warnings 
warnings.filterwarnings('ignore') 


torch.manual_seed(10) 
if torch.cuda.is_available(): 
    torch.cuda.manual_seed(10) 




epochs = 10 
iters_per_epoch = 10 




import os 
try: 
    os.mkdir('./torchmodels') 
except: 
    pass 





gt_data = load_data() 


teacher_models = [MLRM(), DecisionTree()] 

# train teachers 
i = 0 
for teacher in teacher_models: 
    teacher.train(df=gt_data, seed=10+i) 
    i += 1 



# final model 
model = TorchModel(device=device) 
optimizer = torch.optim.AdamW(params=model.parameters(), lr=1e-4)
mseloss = torch.nn.MSELoss() 

x_cols = ['singaporean', 'race_chinese', 'race_malay', 'race_others', 'female', 'dist', 'IPSICU_match'] 
y_col = 'rating' 

def test(epoch_num): 
    losses = [] 
    corrects = [] 

    preds = [] 

    for i in range(len(gt_data)): 
        in_data = torch.tensor(gt_data.loc[i, x_cols].values.astype(np.float32), dtype=torch.float32, device=device) 
        out_ans = float(gt_data.loc[i, y_col]) 
        #ans_arr = np.zeros(6) 
        #ans_arr[out_ans] = 1 
        #ans_arr = torch.tensor(ans_arr, dtype=torch.float32, device=device)

        with torch.no_grad(): 
            out = model(in_data) 
            
            # loss 
            loss = mseloss(out, torch.tensor([out_ans], dtype=torch.float32, device=device)) 
            losses.append(loss.item()) 

            # accuracy 
            pred = round(out.item()) 
            corrects.append(int(pred==round(out_ans)))
            preds.append(preds) 

        
    print("EPOCH {} TEST LOSS: {:.4f} (STD: {:.4f})".format(epoch_num, np.mean(losses), np.std(losses)))
    print("EPOCH {} TEST ACCURACY: {:.4f}".format(epoch_num, sum(corrects))) 
    print() 

    return np.mean(losses), np.mean(corrects), preds 
    

# train with mean softlabels 
train_losses = [] 
test_losses = [] 
test_accuracies = [] 
test_preds = [] 
gen = data_generator(return_dict=False) 
for epoch in range(1, 1+epochs): 
    epoch_losses = [] 
    for sample_num in range(iters_per_epoch): 
        sample = np.array(next(gen))
        reshaped_sample = sample.reshape(1, 7)

        ress = [] 
        for teacher in teacher_models: 
            ress.append(teacher.predict(reshaped_sample)[0]) 
        ans = round(np.mean(ress)) # this is the number 
        ans = min(max(ans, 0), 5) 
        #ans_arr = np.zeros(6) 
        #ans_arr[ans] = 1 

        # train model on this 
        optimizer.zero_grad() 
        out = model(torch.tensor(sample, device=device, dtype=torch.float32)) 
        loss = mseloss(out, torch.tensor(ans, dtype=torch.float32, device=device))
        loss.backward() 
        optimizer.step() 

        epoch_losses.append(loss.item()) 
    
    print("EPOCH {} TRAIN LOSS: {:.4f}".format(epoch, np.mean(epoch_losses)))
    train_losses.append(np.mean(epoch_losses)) 

    if epoch%5 == 0: 
        tl, ta, tp = test(epoch) 
        test_losses.append(tl) 
        test_accuracies.append(ta) 
        test_preds.append(tp) 

        torch.save(model, './torchmodels/torchmodel_epoch{:02d}.pt'.format(epoch))



# graph the change in loss and accuracy with epoch 
import matplotlib.pyplot as plt 

fig, ax1 = plt.subplots() 

plt.title("Graph of loss and accuracy against epoch")

ax2 = ax1.twinx() 

train_xs = list(range(1, epochs+1))
ax1.plot(train_xs, train_losses, color='tab:green', label='Train') 

test_xs = list(range(5, epochs+2, 5)) 
ax1.plot(test_xs, test_losses, color='tab:blue', label='Test') 

ax2.plot(test_xs, test_accuracies, color='tab:red')

ax1.set_ylabel('CrossEntropy Loss', color='tab:blue') 
ax2.set_ylabel('Accuracy', color='tab:red')


plt.legend() 
plt.show() 


# save test preds 
with open('./torchmodels/test_preds.txt', 'w') as fout: 
    fout.write(str(test_preds)) 
    fout.write('\n') 


