def remove_fields(update_data: dict, *field_names):
    for field in field_names:
        update_data.pop(field, None)
