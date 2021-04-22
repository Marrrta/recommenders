import numpy as np
import pandas as pd

print('Setting up the recommender...')

books = pd.read_csv('Books.csv', dtype = 'object')
books.set_index('ISBN', inplace = True)
users = pd.read_csv('Users.csv', low_memory = False,  dtype={'User-ID': 'object', 'Location': 'object', 'Age': 'float64'})
ratings = pd.read_csv('Ratings.csv', low_memory = False, dtype= {'User-ID': 'object', 'ISBN': 'object', 'Book-Rating': 'int64'})

cnt_by_isbn = ratings.groupby('ISBN')['Book-Rating'].count().reset_index()
isbns = cnt_by_isbn[cnt_by_isbn['Book-Rating']> cnt_by_isbn['Book-Rating'].quantile(0.8)]['ISBN']
cnt_by_uid = ratings.groupby('User-ID')['Book-Rating'].count().reset_index()
users = cnt_by_uid[cnt_by_uid['Book-Rating']> cnt_by_uid['Book-Rating'].quantile(0.8)]['User-ID']
ratings_pareto = ratings[(ratings['ISBN'].isin(isbns)) & (ratings['User-ID'].isin(users)) & (ratings['Book-Rating']>0)]
ur_matrix = ratings_pareto.pivot_table(index = 'User-ID', columns = 'ISBN', values = 'Book-Rating')

def distance_users(user1, user2):
    user1vec = ur_matrix[ur_matrix.index == user1]
    user2vec = ur_matrix[ur_matrix.index == user2]
    distance_den = ur_matrix.shape[1]
    distance_nom = ur_matrix.shape[1]
    for _ in range(ur_matrix.shape[1]):
        try:
            if user1vec[_] == user2vec[_]:
                distance_nom -= 1
            elif user1vec[_].isna() and user2vec[_].isna():
                distance_nom -= 1
            else:
                pass
        except:
            pass
    return distance_nom/distance_den

def find_n_similar(user, n=10):
    distances = {}
    for other_user in ur_matrix.index: # if function is super slow, switch from ur_matrix to ur_matrix_slim = ur_matrix.sample(frac = 0.1)
        if other_user == user:
            pass
        else:
            distances[other_user] = distance_users(user, other_user)
    distances_df = pd.DataFrame(data = distances.values(), index = distances.keys(), columns = ['dist']).sort_values(['dist'])

    return list(distances_df.head(n).index)

def find_m_recommendations(user, m, n=10):
    books_read = list(ur_matrix[ur_matrix.index == user].dropna(axis = 1).columns)
    #similar_users = find_n_similar(user, n)
    similar_users = [211307, 208786, 262635]
    avg_ratings = ur_matrix[ur_matrix.index.isin(similar_users)].aggregate(['mean']).drop(columns = books_read)
    avg_ratings_sorted = avg_ratings.T.sort_values('mean', ascending = False)
    top_m = avg_ratings_sorted.index[:m]
    m_books = books[books.index.isin(top_m)][['Book-Title', 'Book-Author']]
    return m_books

print('Please provide your information:')
print("")

input1 = input("What is your user id? ")
print("")
input2 = input("How many recommended books should we show? ")
print("")

print('Please be patient, your recommendations will display shortly!')

print(find_m_recommendations(user = input1, m = int(input2)))
