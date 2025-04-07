import pandas as pd
import uuid

def load_and_prepare_data(input_file: str, output_file: str):
    '''load json file, create unique id, ... '''
    df = pd.read_json(input_file)

    # Create primary ID
    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]

    # Reorder columns
    new_order = [
        'id', 'period', 'duoarea', 'area-name', 'product', 'product-name',
        'process', 'process-name', 'series', 'series-description', 'value', 'units']
    df = df.reindex(columns=new_order)

    # Save to JSON
    df.to_json(output_file, orient='records', lines=True)
    sample = df.sample(100)
    sample.to_json('sample.json', orient='records', lines=True)

    return df

def analize_price_trend(df):
    pass

def validate_data(df):
    pass

if __name__ == "__main__":
    df = load_and_prepare_data('eia_final_raw.json', 'data.json')
