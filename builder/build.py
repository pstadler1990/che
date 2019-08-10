class Builder:

    def __init__(self):
        pass

    """
    Build process:
    
    1. Read all meta and page files from the specified input folder
    2. Log: Check if file already exists in log
        - read contents
        - create hash over contents
        - if not in log yet:
            - create entry from file
            - version: 1
            - if page file:
                - Create references meta information (depending on file format)
                    - Store references meta in entry (find entry)
        - if in log already:
            - compare hashes
            - if no change:
                - skip file
            - if change:
                - add to change list
    3. 
    """