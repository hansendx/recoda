""" Module to share commonly used functionality in the analyse package. """

import glob

def search_filename(
        base_folder: str,
        file_name: str,
        recursive_flag: bool = True
) -> dict:
    """ Return a list of paths to files searched and found.


    :param base_folder: The full path to the Folder, that should be searched through.
    :param file_name:   File name or glob of the item to search for.
    :returns:           A List with full pathes to files matching the file_name.
    """

    if recursive_flag:
        _recursive_glob = '{base}/**/{file}'.format(
            base=base_folder,
            file=file_name
        )

        _findings = glob.glob(_recursive_glob, recursive=recursive_flag)
    else:
        _glob = '{base}/{file}'.format(
            base=base_folder,
            file=file_name
        )
        _findings = glob.glob(_glob)


    return _findings