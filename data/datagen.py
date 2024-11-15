# these will be the columns that we'll be generating unlabelled data for 

import random 

random.seed(10) 


# for dist 
# values for mean and std were gotten from dist.py 
dist_mean = 10.115384615384615 
dist_std = 4.8482901274328984


def data_generator(return_dict=True, x_cols=['singaporean', 'race_chinese', 'race_malay', 'race_others', 'female', 'dist', 'IPSICU_match'] ): 
    # if return_dict==False, then it'll return a list instead. 
    while True: 
        d = [] 

        # decide race first 
        a = random.random() 
        if (a<0.8): 
            race = 'chinese' 
        elif (a < 0.95): 
            race = 'malay' 
        else: 
            race = 'others' 

        for col in x_cols: 
            if col in ['singaporean', 'race_chinese', 'race_malay', 'race_others', 'female', 'IPSICU_match', 'recommend']: 
                # it's an int 
                if col == 'singaporean': 
                    d.append(1) # there's like no other thing 
                elif col in ['female', 'recommend', 'IPSICU_match']: # these have high chance of being True 
                    d.append(int(random.random() > 0.8)) 
                elif 'race' in col: 
                    d.append(int(eval('race == "{}"'.format(col[5:]), locals()))) 
            elif col == 'dist': 
                d.append(random.gauss(dist_mean, dist_std)) 
            else: 
                raise ValueError("'{}' is not a supported columm yet in data_generator.".format(col)) 
            
        if return_dict: 
            dct = {} 
            for i in range(len(x_cols)): 
                dct[x_cols[i]] = d[i] 
            yield dct 
        else: 
            yield d 


if __name__=='__main__': 
    # test generator a bit 
    import pandas as pd 

    gen = data_generator(return_dict = True) 
    test = [next(gen) for _ in range(15)] 
    df = pd.DataFrame(test) 
    print(df) 



    # now try predicting 
    from mlrm import MLRM 
    model = MLRM(save_path='mlrm.pkl') 

    # just in case 
    if not model.trained: 
        model.train() 
    
    print("DF") 
    print(model.predict(df)) 

    # see if this other way of geenrating data works 
    import numpy as np 
    g = data_generator(False) 
    print("list datagen")
    print(np.array(next(g)).shape)
    print(model.predict(np.array(next(g)).reshape(1, 7))) 
    

