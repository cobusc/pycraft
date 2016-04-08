block_types={}

def register_block(name):
    print("name: "+name)
    def wrapper(block):
        global block_types
        print(block)
        if hasattr(block_types, name):
            print("WARNING: block of type {name} already exists. Replacing {orig} with {new}".format(
                    name=name, orig=block_types[name], new=func
                )
            )
        block_types[name]=block
        return block
    return wrapper