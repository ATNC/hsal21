## Steps to Deploy

1. **Ensure Configuration Files are Correctly Placed:**

   Place the `my.cnf` files correctly at `./conf/m/my.cnf`, `./conf/s1/my.cnf`, and `./conf/s2/my.cnf`.

2. **Start Containers:**

   Start the containers with the following command:

   ```
   docker-compose up -d
   ```

3. **Master-Slave Setup Commands**

   Connect to the master (`mysql-m`) and create the replication user:

   ```
   docker exec -it mysql-m mysql -u root -p
   ```

   Inside the MySQL shell, run:

   ```
   CREATE USER 'replicator'@'%' IDENTIFIED WITH mysql_native_password BY 'replica_password';
   GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
   FLUSH PRIVILEGES;

   -- Get the binary log file name and position
   SHOW MASTER STATUS;
   ```

4. **Configure the Slaves (`mysql-s1` and `mysql-s2`):**

   Connect to the first slave:

   ```
   docker exec -it mysql-s1 mysql -u root -p
   ```

   Inside the MySQL shell, run:

   ```
   STOP SLAVE;
   CHANGE MASTER TO
     MASTER_HOST='mysql-m',
     MASTER_USER='replicator',
     MASTER_PASSWORD='replica_password',
     MASTER_LOG_FILE='mysql-bin.000001',  -- Use the correct log file and position
     MASTER_LOG_POS=12345;  -- Use the correct log position

   START SLAVE;
   ```

   Then connect to the second slave:

   ```
   docker exec -it mysql-s2 mysql -u root -p
   ```

   Inside the MySQL shell, run:

   ```
   STOP SLAVE;
   CHANGE MASTER TO
     MASTER_HOST='mysql-m',
     MASTER_USER='replicator',
     MASTER_PASSWORD='replica_password',
     MASTER_LOG_FILE='mysql-bin.000001',  -- Use the correct log file and position
     MASTER_LOG_POS=12345;  -- Use the correct log position

   START SLAVE;
   ```

5. **Verify the Replication Status:**

   Verify the replication status on the first slave:

   ```
   docker exec -it mysql-s1 mysql -u root -p
   SHOW SLAVE STATUS\\G;
   ```

   Verify the replication status on the second slave:

   ```
   docker exec -it mysql-s2 mysql -u root -p
   SHOW SLAVE STATUS\\G;
   ```

## Stopping Slave on `mysql-s1`

To stop the replication on `mysql-s1`, follow these steps:

1. **Stop Slave on `mysql-s1`:**

   Connect to the first slave:

   ```
   docker exec -it mysql-s1 mysql -u root -p
   ```

   Inside the MySQL shell, run:

   ```
   STOP SLAVE;
   SHOW SLAVE STATUS\\G;
   ```

## Removing a Column in the Database on a Slave Node

To remove a column in the database on a slave node (e.g., `mysql-s1`), follow these steps:

1. **Connect to the Slave Node:**

   ```
   docker exec -it mysql-s1 mysql -u root -p
   ```

2. **Remove a Column from the Middle of the Table:**

   Assuming you have a table named `example_table`, run:

   ```
   ALTER TABLE example_table DROP COLUMN column_name;
   ```

3. **Remove the Last Column from the Table:**

   Assuming you have a table named `example_table`, run:

   ```
   ALTER TABLE example_table DROP COLUMN last_column_name;
   ```

## Error Handling

While performing operations on the slave node, you might encounter the following error:

```
Replica SQL for channel '': Worker 1 failed executing transaction 'ANONYMOUS' at source log mysql-bin.000004, end_log_pos 4800; Column 1 of table 'master_db.replication_table' cannot be converted from type 'int' to type 'timestamp', Error_code: MY-013146
```

This error occurs because dropping a column on the slave node causes a mismatch with the master node's schema, leading to a replication failure.

## Conclusion

After completing these steps, you will have set up a MySQL master-slave replication environment using Docker Compose. If you need to stop the replication on any of the slaves, you can do so by connecting to the slave container and executing the `STOP SLAVE` command in the MySQL shell.

For example, to stop the replication on `mysql-s1`:

```
# Connect to the first slave
docker exec -it mysql-s1 mysql -u root -p
```

Inside the MySQL shell, run:

```
STOP SLAVE;
SHOW SLAVE STATUS\\G;
```

You might modify the database schema on a slave node, such as removing columns from a table. This should be done with caution as it can lead to inconsistencies between the master and the slave nodes. It is recommended to make schema changes on the master and let them replicate to the slaves to ensure consistency.

An error can occur when dropping a column on the slave node, which causes a replication failure due to a schema mismatch with the master node. It is crucial to avoid making schema changes directly on the slave nodes.

Stopping the slave halts the replication process for that specific slave, but the master and other slaves (if any) continue to function normally. You can start the replication again using the `START SLAVE` command if needed.

This setup is beneficial for load balancing, read scalability, and data redundancy. Proper monitoring and management of the replication process are essential to ensure data consistency and availability.
