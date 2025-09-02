-- Adiciona colunas de histórico à tabela 'chamado' (MySQL 8+)
ALTER TABLE `chamado`
  ADD COLUMN IF NOT EXISTS `status_assumido_por_id` INT NULL,
  ADD COLUMN IF NOT EXISTS `status_assumido_em` DATETIME NULL,
  ADD COLUMN IF NOT EXISTS `concluido_por_id` INT NULL,
  ADD COLUMN IF NOT EXISTS `concluido_em` DATETIME NULL,
  ADD COLUMN IF NOT EXISTS `cancelado_por_id` INT NULL,
  ADD COLUMN IF NOT EXISTS `cancelado_em` DATETIME NULL;

-- Opcional: criar FKs (remova se não desejar)
-- ALTER TABLE `chamado`
--   ADD CONSTRAINT `fk_chamado_assumido_por` FOREIGN KEY (`status_assumido_por_id`) REFERENCES `user` (`id`),
--   ADD CONSTRAINT `fk_chamado_concluido_por` FOREIGN KEY (`concluido_por_id`) REFERENCES `user` (`id`),
--   ADD CONSTRAINT `fk_chamado_cancelado_por` FOREIGN KEY (`cancelado_por_id`) REFERENCES `user` (`id`);
