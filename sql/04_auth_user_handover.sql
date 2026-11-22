-- Section 1 — run BEFORE `migrate` (one-off)
ALTER TABLE accounts_userprofile        DROP FOREIGN KEY fk_userprofile_user;
ALTER TABLE accounts_customerprofile    DROP FOREIGN KEY fk_customerprofile_user;
ALTER TABLE catalog_vendor              DROP FOREIGN KEY fk_vendor_user;
ALTER TABLE cart_cart                   DROP FOREIGN KEY fk_cart_user;
ALTER TABLE orders_order                DROP FOREIGN KEY fk_order_user;
ALTER TABLE favorites_favoriteproduct   DROP FOREIGN KEY fk_favproduct_user;
ALTER TABLE favorites_favoritevendor    DROP FOREIGN KEY fk_favvendor_user;
DROP TABLE auth_user;

-- Section 2 — run AFTER `migrate` (re-points the FKs at the new auth_user)
ALTER TABLE accounts_userprofile         ADD CONSTRAINT fk_userprofile_user        FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE accounts_customerprofile     ADD CONSTRAINT fk_customerprofile_user    FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE catalog_vendor               ADD CONSTRAINT fk_vendor_user             FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE cart_cart                    ADD CONSTRAINT fk_cart_user               FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE orders_order                 ADD CONSTRAINT fk_order_user              FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE favorites_favoriteproduct    ADD CONSTRAINT fk_favproduct_user         FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE favorites_favoritevendor     ADD CONSTRAINT fk_favvendor_user          FOREIGN KEY (user_id) REFERENCES auth_user (id);