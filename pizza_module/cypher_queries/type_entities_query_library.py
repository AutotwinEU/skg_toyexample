from promg import Query


def create_properties_str(properties):
    return ", ".join(f"{key}: {value}" for key, value in properties.items())


mapping_entity_type_to_labels = {
    "PZ": ["Pizza"],
    "PACK": ["Pack"],
    "BOX": ["Box", "Run"],
    "PAL": ["Pallet"]
}


class TypeEntityQueryLibrary:

    @staticmethod
    def create_generic_entity_types(entity_labels, entity_type_properties, entity_properties):
        entity_type_properties = create_properties_str(entity_type_properties)
        entity_properties = create_properties_str(entity_properties)
        if entity_properties != "":
            entity_properties = "{" + entity_properties + "}"
        if entity_type_properties != "":
            entity_type_properties = "{" + entity_type_properties + "}"

        query_str = '''
            MATCH (n:$entity_labels $entity_properties)
            MATCH (et:EntityType $entity_type_properties)
            MERGE (n) - [:IS_OF_TYPE] -> (et)
        '''

        return Query(
            query_str=query_str,
            template_string_parameters={
                "entity_labels": ":".join(entity_labels),
                "entity_type_properties": entity_type_properties,
                "entity_properties": entity_properties
            }
        )

    @staticmethod
    def create_associate_dissociate_type(station_properties, sensor_properties, entity_type_properties):
        station_properties = create_properties_str(station_properties)
        sensor_properties = create_properties_str(sensor_properties)

        if "XXXX" in entity_type_properties["code"]:  # entity type is typed
            generic_code = entity_type_properties["code"].split("_")[0].strip('"')
            if "simulated" in entity_type_properties:
                entity_type_properties = f'''WHERE et.code <> "{generic_code}" and et.simulated = True'''
            else:
                entity_type_properties = f'''WHERE et.code <> "{generic_code}"'''
        else:  # entity type is untyped
            generic_code = entity_type_properties["code"].strip('"')
            entity_type_properties = "{" + create_properties_str(entity_type_properties) + "}"

        entity_labels = mapping_entity_type_to_labels[generic_code]

        query_str = '''
            MATCH (e) - [:OCCURRED_AT] -> (station:Station {$station_properties})
            MATCH (e) - [:EXECUTED_BY] -> (sensor:Sensor {$sensor_properties})
            MATCH (e) - [:ACTS_ON] -> (n:$entity_labels) - [:IS_OF_TYPE] -> (et:EntityType $entity_type_properties)
            MERGE (e) - [:ASSOCIATE_TYPE] -> (et)        
        '''

        return Query(
            query_str=query_str,
            template_string_parameters={
                "station_properties": station_properties,
                "sensor_properties": sensor_properties,
                "entity_type_properties": entity_type_properties,
                "entity_labels": ":".join(entity_labels)
            }
        )
