from tqdm import tqdm
import pandas as pd
import os
from pdb import set_trace
import shutil


def lab_gen(mode='train'):
    '''
    mode: train, val, test

    '''

    with open("Raw_DataSets/class.names", 'r') as f:
        classes = f.read().splitlines()
        classes = [it.replace('_', ' ') for it in classes]
        class_id_dict = {cls: num for num, cls in enumerate(classes)}

    lab_nm2id = pd.read_csv(
        "./Raw_DataSets/class-descriptions-boxable.csv", names=['id', 'names'])

    img_dir = f"custom_dataset/images/{mode}"
    lab_dir = f"custom_dataset/labels/{mode}"

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    if not os.path.exists(lab_dir):
        os.makedirs(lab_dir)

    lab_nm2id_dict = pd.Series(
        lab_nm2id.names.values, index=lab_nm2id.id).to_dict()

    # Load annotations
    train_ann = pd.read_csv(f"./Raw_DataSets/{mode}-annotations-bbox.csv")

    lab_id2nm_ser = train_ann.LabelName.map(lab_nm2id_dict.get)

    train_ann = train_ann.loc[lab_id2nm_ser.isin(classes)]
    train_ann['lab_id'] = lab_id2nm_ser.map(class_id_dict)
    train_ann.lab_id = train_ann.lab_id.astype('int')

    for img_id in tqdm(train_ann.ImageID.unique()):
        try:
            # if os.path.exists(f'{lab_dir}/{img_id}.txt'):
            #     continue
            shutil.copy(os.path.join(
                f"Raw_DataSets/{mode}_images/{img_id}.jpg"), img_dir)

            train_ann_sub = train_ann.loc[train_ann.ImageID == img_id].copy()
            cords_arr = train_ann_sub[["XMin", "XMax", "YMin", "YMax"]].values

            cords_arr[:, 0] = (cords_arr[:, 1]+cords_arr[:, 0])/2
            cords_arr[:, 1] = (cords_arr[:, 3]+cords_arr[:, 2])/2
            cords_arr[:, 2] = cords_arr[:, 1]-cords_arr[:, 0]
            cords_arr[:, 3] = cords_arr[:, 3]-cords_arr[:, 2]

            lab_ids = train_ann_sub.lab_id.values

            # Start with combining lab_id with xywh values into text file
            with open(f'{lab_dir}/{img_id}.txt', 'w') as f:
                for i in range(len(train_ann_sub)):
                    lin_txt = '\t'.join([str(i)
                                        for i in [lab_ids[i]]+cords_arr[i].tolist()])
                    f.write(f"{lin_txt}\n")
        except:
            print(f"skipping: {img_id}")
