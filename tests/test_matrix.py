from src.matrix import Matrix, Posting

def test_matrix():
    # matrix = Matrix(breakpoints = [])
    
    # matrix.add("test", Posting(0, 2), "0")
    # matrix.add("test", Posting(1, 5), "1")
    # matrix.add("test", Posting(3, 1), "3")
    
    # print(matrix)
    
    # matrix.save()
    # matrix.finalize()
    p = Posting(0, 2, True, True, False)
    print(p.sortable())