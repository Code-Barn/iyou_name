            # Extract name information safely, prioritizing birth names
            name_obj = getattr(record, "name", None)
            birth_name_obj = None
            if name_obj:
                # Check if there are multiple name records
                name_records = record.sub_tags("NAME")
                for name_record in name_records:
                    # Check for TYPE BIRTH
                    type_tag = name_record.sub_tag("TYPE")
                    if type_tag and hasattr(type_tag, "value") and str(type_tag.value).upper() == "BIRTH":
                        birth_name_obj = name_record
                        break

                # Use birth name if available, otherwise use the first name
                if birth_name_obj:
                    given_name = getattr(birth_name_obj, "given", "")
                    surname = getattr(birth_name_obj, "surname", "")
                    full_name = getattr(
                        birth_name_obj, "format", lambda: f"{given_name} {surname}"
                    )()
                else:
                    given_name = getattr(name_obj, "given", "")
                    surname = getattr(name_obj, "surname", "")
                    full_name = getattr(
                        name_obj, "format", lambda: f"{given_name} {surname}"
                    )()
