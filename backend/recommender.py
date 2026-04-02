import pandas as pd
from backend.rating_based import get_rating_based_recommendations
from backend.collaborative_filtering import get_collaborative_recommendations
from backend.content_filtering import get_content_based_recommendations, get_content_based_search_recommendations

def get_combined_recommendations(user_id=None, is_new_user=False, current_product_id=None, search_query=None, top_n=5, data_path='cleaned_data.csv'):
    """
    Combine all recommendation approaches.
    Logic:
    IF new user: use rating-based
    ELSE: use collaborative + content
    """
    if is_new_user or user_id is None:
        # Rating-based recommendations for new users
        print("Fetching rating-based recommendations for new user...")
        return get_rating_based_recommendations(top_n=top_n, min_reviews=2, data_path=data_path)
    
    else:
        # For returning users, use collaborative filtering as the baseline
        print(f"Fetching collaborative recommendations for User {user_id}...")
        collab_recs = get_collaborative_recommendations(user_id=user_id, top_n=top_n, data_path=data_path)
        
        # If the user is viewing a specific product, add content-based recommendations
        if current_product_id is not None:
            print(f"Fetching content-based recommendations for Product {current_product_id}...")
            content_recs = get_content_based_recommendations(product_id=current_product_id, top_n=top_n, data_path=data_path)
            
            if isinstance(collab_recs, pd.DataFrame) and isinstance(content_recs, pd.DataFrame):
                combined = pd.concat([collab_recs, content_recs]).drop_duplicates(subset=['ProdID'])
                collab_recs = combined.head(top_n).reset_index(drop=True)
            elif isinstance(content_recs, pd.DataFrame):
                collab_recs = content_recs
                
        # If the user has a search history, inject those items
        if search_query:
            print(f"Fetching content-based recommendations based on Search History: '{search_query}'...")
            search_recs = get_content_based_search_recommendations(search_query=search_query, top_n=top_n, data_path=data_path)
            if isinstance(search_recs, pd.DataFrame) and not search_recs.empty:
                if isinstance(collab_recs, pd.DataFrame):
                    combined = pd.concat([search_recs, collab_recs]).drop_duplicates(subset=['ProdID'])
                    collab_recs = combined.head(top_n).reset_index(drop=True)
                else:
                    collab_recs = search_recs
        
        return collab_recs

if __name__ == '__main__':
    print("Testing new user scenario:")
    print(get_combined_recommendations(is_new_user=True))
    print("\n-------------------------------\n")
    print("Testing existing user scenario:")
    # Assuming user 1705 exists
    print(get_combined_recommendations(user_id=1705, is_new_user=False))
