from pizza_module.cypher_queries.type_entities_query_library import TypeEntityQueryLibrary as tql


class EntityTypeModule:
    def __init__(self, db_connection, is_simulated=False):
        self.connection = db_connection
        self.is_simulated = is_simulated

    def create_sys_id_and_simulated_properties(self, sys_id=None):
        if sys_id is not None:
            properties = {"sysId": f'"{sys_id}"'}
        else:
            properties = {}
        if self.is_simulated:
            properties["simulated"] = True
        return properties

    def create_generic_entity_types(self):
        generic_entity_types = [{"entity_labels": ["Box", "Run"], "entity_code": '"BOX"'},
                                {"entity_labels": ["Pallet"], "entity_code": '"PAL"'}]
        for generic_entity_type in generic_entity_types:
            entity_type_properties = self.create_sys_id_and_simulated_properties()
            entity_type_properties["code"] = generic_entity_type["entity_code"]
            entity_properties = self.create_sys_id_and_simulated_properties()
            self.connection.exec_query(
                tql.create_generic_entity_types,
                **{
                    "entity_labels": generic_entity_type["entity_labels"],
                    "entity_type_properties": entity_type_properties,
                    "entity_properties": entity_properties
                }
            )

    def create_associate_dissociate_type_rules(self):
        rules = [{"station_id": "PizzaSource",
                  "sensor_type": '"EXIT"',
                  "code": '"PZ_XXXX"'},
                 {"station_id": "PackStation",
                  "sensor_type": '"EXIT"',
                  "code": '"PACK_XXXX"'},
                 {"station_id": "BoxStation",
                  "sensor_type": '"EXIT"',
                  "code": '"BOX_XXXX"'},
                 {"station_id": "PalletStation",
                  "sensor_type": '"EXIT"',
                  "code": '"PAL_XXXX"'},
                 {"station_id": "PalletSource",
                  "sensor_type": '"EXIT"',
                  "code": '"PAL"'},
                 {"station_id": "RefurbishProcess",
                  "sensor_type": '"EXIT"',
                  "sensor_subtype": '"AP"',
                  "code": '"BOX"'},
                 {"station_id": "NewBoxWarehouse",
                  "sensor_type": '"ENTER"',
                  "code": '"BOX"'},
                 {"station_id": "RefurbishedBoxWarehouse",
                  "sensor_type": '"ENTER"',
                  "code": '"BOX"'}
                 ]

        for rule in rules:
            station_properties = self.create_sys_id_and_simulated_properties(sys_id=rule["station_id"])
            sensor_properties = self.create_sys_id_and_simulated_properties()
            sensor_properties["type"] = rule["sensor_type"]
            if "sensor_subtype" in rule:
                sensor_properties["subType"] = rule["sensor_subtype"]
            entity_type_properties = self.create_sys_id_and_simulated_properties()
            entity_type_properties["code"] = rule["code"]
            self.connection.exec_query(
                tql.create_associate_dissociate_type,
                **{
                    "station_properties": station_properties,
                    "sensor_properties": sensor_properties,
                    "entity_type_properties": entity_type_properties
                }
            )
