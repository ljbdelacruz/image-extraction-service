#!/bin/sh

npx prisma migrate deploy
npx prisma generate

npx knex migrate:latest

$@
