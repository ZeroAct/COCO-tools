import os, random, copy, json
from pycocotools.coco import COCO


class COCOManager:

    def __init__(self, coco, root_dir=''):

        self.root_dir  = root_dir

        if isinstance(coco, str):
            assert os.path.isfile(coco)
            self.coco = COCO(coco)
        
        elif isinstance(coco, COCO):
            self.coco = coco
        
        print(f"Found {len(self.coco.imgs)} images, {len(self.coco.anns)} annotations, {len(self.coco.cats)} categories!")
    
    #=== Getter ===#
    def get_cats(self) -> dict:
        """
        { catid: {'supercategory': , 'id': catid, 'name': } }
        """
        return self.coco.cats
    
    def get_imgs(self) -> dict:
        """
        { imgid: {'id': imgid, ~~~~}}
        """
        return self.coco.imgs
    
    def get_imgs_dict(self, ids=[]) -> dict:
        return {id: self.coco.imgs[id] for id in ids}

    def get_anns_dict(self, ids=[]) -> dict:
        return {id: self.coco.anns[id] for id in ids}
    
    def get_nums(self):
        return len(self.coco.imgs), len(self.coco.anns), len(self.coco.cats)
    
    #=== Setter ===#
    def set_cats(self, cats: dict):
        """
        { catid: {'supercategory': , 'id': catid, 'name': } }
        """
        self.coco.cats = cats
        self.coco.dataset['categories'] = list(cats.values())

    def set_imgs(self, imgs: dict):
        """
        { imgid: {'id': imgid, ~~~~}}
        """
        self.coco.imgs = imgs
        self.coco.dataset['images'] = list(imgs.values())
    
    def set_anns(self, anns: dict):
        """
        { annid: {'id': annid, ~~~~}}
        """
        self.coco.anns = anns
        self.coco.dataset['annotations'] = list(anns.values())
    
    #=== Functions ===#
    def train_val_split(self, train_ratio=0.8, seed=123):

        imgs    = self.get_imgs()
        img_ids = list(imgs.keys())
        img_num = len(img_ids)

        random.seed(seed)
        random.shuffle(img_ids)

        train_img_ids = img_ids[:int(img_num * train_ratio)]
        val_img_ids   = img_ids[int(img_num * train_ratio):]

        train_coco = copy.deepcopy(self)
        train_coco.set_imgs(self.get_imgs_dict(train_img_ids))
        train_coco.set_anns(self.get_anns_dict(self.coco.getAnnIds(train_img_ids)))

        val_coco = copy.deepcopy(self)
        val_coco.set_imgs(self.get_imgs_dict(val_img_ids))
        val_coco.set_anns(self.get_anns_dict(self.coco.getAnnIds(val_img_ids)))

        return train_coco, val_coco

    def save(self, save_path):
        if os.path.isfile(save_path):
            print('FileExist')
        else:
            os.makedirs(os.path.split(save_path)[0], exist_ok=True)
            with open(save_path, 'w') as f:
                json.dump(self.coco.dataset, f)




if __name__ == "__main__":

    coco_path = "d:/data/coco/annotations/instances_val2017.json"

    coco = COCOManager(coco_path)
    train_coco, val_coco = coco.train_val_split()
    train_coco.save('./train.json')
    val_coco.save('./val.json')

    train_coco = COCOManager('train.json')
    val_coco   = COCOManager('val.json')