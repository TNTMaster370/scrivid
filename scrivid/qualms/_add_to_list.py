def add_qualm(qualms, cls, index, *additional_args):
    new_qualm = cls(index, *additional_args)
    relevant_qualm = None

    for qualm in reversed(qualms):
        if type(qualm) is cls and qualm == new_qualm:
            relevant_qualm = qualm
            break

    if relevant_qualm is None:
        qualms.append(new_qualm)
        return

    if relevant_qualm.index.end != index - 1:
        qualms.append(new_qualm)
        return

    relevant_qualm.index.end += 1
