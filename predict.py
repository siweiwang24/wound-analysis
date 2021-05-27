"""Make predictions using encoder."""
# pylint: disable=no-name-in-module
from json import load
from typing import Tuple
import numpy as np  # type: ignore
from tensorflow.keras.layers import Layer  # type: ignore
from data_process import load_data
from model import get_encoder_model, get_siamese_model
from model import ENCODER_FILE, HYP_FILE, SIAMESE_FILE
from center import CENTERS_FILE


def load_encoder(in_shape: Tuple[int, ...]):
    """Load encoder with weights."""
    encoder = get_encoder_model(in_shape)
    encoder.load_weights(ENCODER_FILE)
    return encoder


def get_dense(in_shape: Tuple[int, ...]) -> Layer:
    """Load final dense layer with weights."""
    siamese = get_siamese_model(in_shape)
    siamese.load_weights(SIAMESE_FILE)
    return siamese.layers[-1]


def test_preds():
    """Test predictions over all images."""
    with open(HYP_FILE) as fin:
        hyp: dict = load(fin)
    images, labels = load_data(hyp)
    encoder = load_encoder(images.shape[1:])
    dense = get_dense(images.shape[1:])
    centers = np.load(CENTERS_FILE)
    zero_one = np.empty_like(labels, dtype=bool)
    for idx, (img, lbl) in enumerate(zip(images, labels)):
        rep = encoder(img[np.newaxis, ...])
        outputs = dense(np.abs(centers - rep))
        pred = np.argmax(outputs)
        zero_one[idx] = (pred == lbl)
    print('Accuracy =', np.count_nonzero(zero_one) / len(zero_one))


if __name__ == '__main__':
    test_preds()
