# Kanji Diffuser

This project fine-tune a stable diffusion model on kanji characters (images) and their definitions (texts) to generate novel kanji characters.
The project was tested using Google Colab with a runtime type of A100. 
Please access this [Colab notebook](https://drive.google.com/file/d/1zDVQnub2mtW_9zobijmq2LlvvNtjVHbl/view?usp=sharing) for the installation, training, and inference.

This repository supports the required `kanjidic_dataset` and the training script `train_text_to_image.py` that you can upload to the cloned diffuser.

## Requirements
The repository requires:
```python
cairosvg==2.7.1
```
  
## Dataset construction
A dataset named `kanjidic_dataset` can be created with:

```
python data_processor.py
```