SET FOREIGN_KEY_CHECKS=0;
ALTER TABLE accounts_userprofile         ADD CONSTRAINT fk_userprofile_user        FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE accounts_customerprofile     ADD CONSTRAINT fk_customerprofile_user    FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE catalog_vendor               ADD CONSTRAINT fk_vendor_user             FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE cart_cart                    ADD CONSTRAINT fk_cart_user               FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE orders_order                 ADD CONSTRAINT fk_order_user              FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE favorites_favoriteproduct    ADD CONSTRAINT fk_favproduct_user         FOREIGN KEY (user_id) REFERENCES auth_user (id);
ALTER TABLE favorites_favoritevendor     ADD CONSTRAINT fk_favvendor_user          FOREIGN KEY (user_id) REFERENCES auth_user (id);
SET FOREIGN_KEY_CHECKS=1;