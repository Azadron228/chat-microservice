-- Create Keycloak DB + user
CREATE USER keycloak WITH PASSWORD 'supersecret';
CREATE DATABASE keycloak OWNER keycloak;

-- Create User Service DB + user
CREATE USER user_service WITH PASSWORD 'user_pass';
CREATE DATABASE "user" OWNER user_service;

-- Create Room Service DB + user
CREATE USER room_service WITH PASSWORD 'room_pass';
CREATE DATABASE room OWNER room_service;
