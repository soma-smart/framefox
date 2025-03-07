
Dans le cas ou il y a une erreur de modif de la migration il faut changer l'ordre dans la migration elle meme 


```bash
(env) (base) rayen@ordinateur-de-rayen:~/Bureau/PROJECT-DEV/SOMA/ONLINE/dev-framefox$ framefox database:create-migration
Exécution de la commande database:create-migration
  Generating /home/rayen/Bureau/PROJECT-DEV/SOMA/ONLINE/dev-framefox/migrations/versions/73810ece40ad_20250307_170900_migration.py ...  done
Fichier de migration '73810ece40ad_20250307_170900_migration.py' créé avec succès.
Vous pouvez maintenant exécuter la commande 'framefox database:upgrade' pour appliquer les mises à jour.
(env) (base) rayen@ordinateur-de-rayen:~/Bureau/PROJECT-DEV/SOMA/ONLINE/dev-framefox$ framefox database:upgrade
Exécution de la commande database:upgrade
Application des migrations...
Erreur lors de la mise à jour: (pymysql.err.OperationalError) (3730, "Cannot drop table 'conversation' referenced by a foreign key constraint 'message_ibfk_1' on table 'message'.")
[SQL: 
DROP TABLE conversation]
(Background on this error at: https://sqlalche.me/e/20/e3q8)
L'application des migrations a échoué.
(env) (base) rayen@ordinateur-de-rayen:~/Bureau/PROJECT-DEV/SOMA/ONLINE/dev-framefox$ 
```