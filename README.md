# 🔄 MapGPT

MapGPT is an innovative open-source tool designed to reformat your source table into a desired target format. It intelligently maps values from your source table while adopting column names and value styles/formats from the target table. This tool is incredibly useful for data scientists, analysts, and anyone who works with data in various formats.

## 🛠️ How It Works

1. **Column Detection and Pruning**: MapGPT first identifies identical columns in the target table and prunes them, effectively reducing the number of parameters the model needs to manage.

2. **RowModel Creation**: The system automatically generates few-shot prompts from the target table. It uses the first row of the source table as an additional input, presenting these to the language model (LLM). To avoid hallucination and enhance accuracy, it randomly omits some cells in the few-shot prompts. Additionally, it shuffles the cells randomly, leveraging the strategy proposed in this [research paper](https://arxiv.org/abs/2210.06280), to prompt the model to decipher cell-column correlations.

3. **CellModel Conversion**: The CellModel takes the intermediate results from the RowModel and converts them into the final row format. This process involves feeding a predetermined number of target rows into the model.

4. **User Customization**: After generating the final row, MapGPT offers users the option to make any desired changes.

5. **Automated Full-table Transformation**: Based on the user's changes (if any), MapGPT applies the transformation across the entire table. Users can then preview the final table before downloading it.

## 🚀 Live Demo

Experience the live demo of MapGPT on our Streamlit app: [MapGPT Streamlit App](https://mapgpt.streamlit.app/)

## 🌟 Features

- Intelligent mapping of table data
- User-driven customization options
- Automated table transformation
- Anti-hallucination and correlation understanding through innovative cell shuffling

## 💾 Installation

```bash
git clone git@github.com:melih-unsal/MapGPT.git
cd MapGPT
pip install -r requirements.txt
```

## Usage 🖥️

To run the app, use the following command:

```bash
streamlit run app.py
```


## 🤝 Contribute

Contributions to the DemoGPT project are welcomed! Whether you're fixing bugs, improving the documentation, or proposing new features, your efforts are highly appreciated. Please check the open issues before starting any work.

> Please read [`CONTRIBUTING`](CONTRIBUTING.md) for details on our [`CODE OF CONDUCT`](CODE_OF_CONDUCT.md), and the process for submitting pull requests to us.

## 📜 License

MapGPT is an open-source project licensed under [MIT License](LICENSE).

---

For any issues, questions, or comments, please feel free to contact us or open an issue. We appreciate your feedback to make MapGPT better.
