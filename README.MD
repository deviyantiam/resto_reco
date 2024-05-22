# Resto Recommendation

## Table of Contents
* [About the Project](#about-the-project)
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#Installation)
    * [Environment Variable](#environment-variable)
* [Author](#author)

<!-- About THE PROJECT -->
## [About The Project](#about-the-project)

This project aims to help people in Nashville find great restaurants easily. We use hybrid method to make personalized recommendations for users.

For model development, you can see the ipynb

- Collaborative Filtering:
Utilizing the Surprise library, we implement collaborative filtering to predict user preferences based on their past ratings and those of similar users. Multiple collaborative filtering algorithms are explored, including Singular Value Decomposition (SVD), Non-negative Matrix Factorization (NMF), and NormalPredictor. Hyperparameter tuning is conducted to optimize model performance, with the selection of the model with the lowest Root Mean Square Error (RMSE) against actual ratings

- Content-Based Filtering:
we use Latent Dirichlet Allocation (LDA) to extract topics from restaurant reviews. By combining these topics with available restaurant categories, we compute similarity scores between restaurants, enabling us to recommend restaurants that align closely with a user's preferences based on past experiences

Handling Cold Start:
For new users lacking sufficient historical data, we tackle the cold start problem by initially recommending restaurants with the highest average ratings within the user's zip code

## [Getting Started](#getting-started)

### [Prerequisites](#prerequisites)
* **Python 3.9+**

### [Installation](#Installation)
After clone the repo, follow instruction below

- Create Env
```
conda create -n reco_app python==3.9.0
conda activate reco_app
pip install -r requirements.txt
```
- Download data [here](https://drive.google.com/drive/folders/1ypTsTb2M23C5g0wh0lJI0NEgwXGVOsKP?usp=drive_link)
- Run streamlit
```
streamlit run app_streamlit.py
```

### [Environment Variable](#environment-variable)
The project is configured via environment variables, i.e. file `.env` but we dont attach it here 

## [Author](#author)
Deviyanti AM [linkedin](https://linkedin.com/in/deviyanti-am)