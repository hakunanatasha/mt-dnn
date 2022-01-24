from transformers import (
    BertConfig, BertModel, BertTokenizer,
    RobertaConfig, RobertaModel, RobertaTokenizer,
    AlbertConfig, AlbertModel, AlbertTokenizer,
    XLMRobertaConfig, XLMRobertaModel, XLMRobertaTokenizer,
    ElectraConfig, ElectraModel, ElectraTokenizer,
    T5Config, T5EncoderModel, T5ForConditionalGeneration, T5Tokenizer,
    DebertaConfig, DebertaModel, DebertaTokenizer,
)

from module.san_model import SanModel
MODEL_CLASSES = {
    "bert": (BertConfig, BertModel, BertTokenizer),
    "roberta": (RobertaConfig, RobertaModel, RobertaTokenizer),
    "albert": (AlbertConfig, AlbertModel, AlbertTokenizer),
    "xlm": (XLMRobertaConfig, XLMRobertaModel, XLMRobertaTokenizer),
    "san": (BertConfig, SanModel, BertTokenizer),
    "electra": (ElectraConfig, ElectraModel, ElectraTokenizer),
    "t5": (T5Config, T5EncoderModel, T5Tokenizer),
    "deberta": (DebertaConfig, DebertaModel, DebertaTokenizer),
    "t5g": (T5Config, T5ForConditionalGeneration, T5Tokenizer),
}