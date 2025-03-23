import pickle
import os

def create_abc_sequence_object(target_size_mb=1):
    target_size_bytes = target_size_mb * 1024 * 1024
    sequence = "abc "
    repetitions = target_size_bytes // len(sequence) + 1
    data = (sequence * repetitions)[:target_size_bytes]
    return data

def save_pickle(obj, filename):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)
    size = os.path.getsize(filename)
    print(f"Objet sauvegardé dans '{filename}' ({size / (1024 * 1024):.2f} Mo)")

if __name__ == "__main__":
    abc_obj = create_abc_sequence_object(target_size_mb=1)
    save_pickle(abc_obj, 'abc_sequence_object.pickle')
