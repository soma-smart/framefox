class RequestListener:
    """
    Classe listener pour gérer les événements liés aux requêtes.
    """

    # def on_request_received(self, payload):
    #     request = payload.get("request")

    #     if request:
    #         method = request.method
    #         url = request.url.path
    #         client = request.client.host
    #         print(f"[Listener] Requête reçue: {method} {url} de {client}")

    # def on_request_completed(self, payload):
    #     response = payload.get("response")
    #     if response:
    #         status_code = response.status_code
    #         print(
    #             f"[Listener] Requête complétée avec le statut: {
    #               status_code}"
    #         )

    # def register_listeners(self, dispatcher):
    #     """
    #     Méthode pour enregistrer les listeners auprès du dispatcher.
    #     """
    #     dispatcher.add_listener("kernel.request_received", self.on_request_received)
    #     dispatcher.add_listener("kernel.request_completed", self.on_request_completed)
