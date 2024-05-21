- Link train model: https://www.kaggle.com/code/iamchaos666/vehicle-king
- Link tải weight best.pt: https://drive.google.com/file/d/1uRB9fCfloHiEbs3Qu0z3CvIDYrbDjHRO/view?usp=sharing

1. Tải weight best.pt, sau đó gán vào biến weight_pt trong file config.yaml
2. Set up môi trường conda 
cd / -> chuyển tới folder vehilce_dert
run:
python setup.py
3. build engine weight
run: python build_engine_weight.py 
4. set up detection range
- cd setup
- run: python setup_range
- bấm w để khởi tạo bbox mới , sau khi chọn bấm w để save, bấm q để quit
5 inferences
run: utils.py -src path_data
