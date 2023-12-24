def add_qualm(qualms, cls, index, *additional_args):
    relevant_qualm = None

    for qualm in reversed(qualms):
        if type(qualm) is cls:
            relevant_qualm = qualm
            break

    if relevant_qualm is None:
        qualms.append(cls(index, *additional_args))
        return

    if relevant_qualm.index.end != index - 1:
        qualms.append(cls(index, *additional_args))
        return

    relevant_qualm.index.end += 1
