from process_discovery import msm_lib as msm


class ProcessDiscoveryLog:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = msm.load_config(self.config_path)

    def get_discovered_proces_model(self, event_log):
        graph = msm.generate_graph(event_log, self.config)
        msm.save_graph(graph, self. config)
        graph = msm.load_graph(self.config)
        msm.show_graph(graph)
        return graph
