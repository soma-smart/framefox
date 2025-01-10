class AuthListener:
    """
    Classe listener pour gérer les événements liés à l'authentification.
    """

    # def on_auth_attempt(self, payload):
    #     request = payload.get("request")
    #     if request:
    #         auth_header = request.headers.get("Authorization")
    #         print(
    #             f"[Listener] Tentative d'authentification avec le header: {
    #               auth_header}"
    #         )

    # def on_auth_result(self, payload):
    #     response = payload.get("response")
    #     if response:
    #         if response.status_code == 200:
    #             print(f"[Listener] Authentification réussie.")
    #         else:
    #             print(f"[Listener] Authentification échouée.")

    # def register_listeners(self, dispatcher):
    #     """
    #     Méthode pour enregistrer les listeners auprès du dispatcher.
    #     """
    #     dispatcher.add_listener("auth.auth_attempt", self.on_auth_attempt)
    #     dispatcher.add_listener("auth.auth_result", self.on_auth_result)
