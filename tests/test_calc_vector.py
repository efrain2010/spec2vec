import os
import gensim
import numpy
import pytest
from matchms import Spectrum
from spec2vec import SpectrumDocument
from spec2vec.calc_vector import calc_vector


def test_calc_vector():
    """Test deriving a document vector using a pretrained network."""
    spectrum = Spectrum(mz=numpy.array([100, 150, 200, 250], dtype="float"),
                        intensities=numpy.array([0.1, 0.1, 0.1, 1.0], dtype="float"),
                        metadata={})

    document = SpectrumDocument(spectrum, n_decimals=1)
    model = import_pretrained_model()
    vector = calc_vector(model, document, intensity_weighting_power=0.5, allowed_missing_percentage=1.0)
    expected_vector = numpy.array([0.08982063, -1.43037023, -0.17572929, -0.45750666, 0.44942236,
                                   1.35530729, -1.8305029, -0.36850534, -0.28393048, -0.34192028])
    assert numpy.all(vector == pytest.approx(expected_vector, 1e-5)), "Expected different document vector."


def test_calc_vector_higher_than_allowed_missing_percentage():
    """Test using a pretrained network and a missing word percentage above allowed."""
    spectrum = Spectrum(mz=numpy.array([11.1, 100, 200, 250], dtype="float"),
                        intensities=numpy.array([0.1, 0.1, 0.1, 1.0], dtype="float"),
                        metadata={})

    document = SpectrumDocument(spectrum, n_decimals=1)
    model = import_pretrained_model()
    assert document.words[0] not in model.wv.vocab, "Expected word to be missing from given model."
    with pytest.raises(AssertionError) as msg:
        calc_vector(model, document, intensity_weighting_power=0.5, allowed_missing_percentage=16.0)

    expected_message_part = "Missing percentage is larger than set maximum."
    assert expected_message_part in str(msg.value), "Expected particular error message."


def test_calc_vector_within_allowed_missing_percentage():
    """Test using a pretrained network and a missing word percentage within allowed."""
    spectrum = Spectrum(mz=numpy.array([11.1, 100, 200, 250], dtype="float"),
                        intensities=numpy.array([0.1, 0.1, 0.1, 1.0], dtype="float"),
                        metadata={})

    document = SpectrumDocument(spectrum, n_decimals=1)
    model = import_pretrained_model()
    vector = calc_vector(model, document, intensity_weighting_power=0.5, allowed_missing_percentage=17.0)
    expected_vector = numpy.array([0.12775915, -1.17673617, -0.14598507, -0.40189132, 0.36908966,
                                   1.11608575, -1.46774333, -0.31442554, -0.23168877, -0.29420064])
    assert document.words[0] not in model.wv.vocab, "Expected word to be missing from given model."
    assert numpy.all(vector == pytest.approx(expected_vector, 1e-5)), "Expected different document vector."


def import_pretrained_model():
    """Helper function to import pretrained word2vec model."""
    repository_root = os.path.join(os.path.dirname(__file__), "..")
    model_file = os.path.join(repository_root, "integration-tests", "test_user_workflow_spec2vec.model")
    return gensim.models.Word2Vec.load(model_file)
