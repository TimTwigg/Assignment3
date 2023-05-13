from src.matrix import Matrix, Posting

def setup_matrix() -> Matrix:
    matrix = Matrix()
    postData = [*enumerate("123456abcdefghijklmnopqrstuvwxyz")]
    for i,l in postData:
        matrix.add(l, Posting(str(i), 5))
    return matrix

def test_matrix():
    matrix = setup_matrix()
    print(matrix)
    
    # test add with updating
    matrix.add("a", Posting("0", 2))
    
    # test removing
    matrix.add("a", Posting("1", 2))
    matrix.remove("b")
    matrix.remove("a", "3")
    
    print(matrix)