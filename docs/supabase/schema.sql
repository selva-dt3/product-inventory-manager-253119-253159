-- Supabase schema for Product Inventory Manager
-- Creates 'products' table, indexes, and trigger to auto-update updated_at.
-- Safe to run multiple times with IF NOT EXISTS guards where possible.

-- Extensions (enable if not already enabled)
-- gen_random_uuid requires pgcrypto (or use uuid-ossp's uuid_generate_v4)
create extension if not exists pgcrypto;
create extension if not exists pg_trgm; -- optional, for trigram index notes below

-- Table: products
create table if not exists public.products (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    sku text not null unique,
    description text,
    price numeric(10,2) not null default 0,
    quantity integer not null default 0,
    image_url text,
    image_path text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Indexes
-- Case-insensitive search on product name
do $$
begin
    if not exists (
        select 1 from pg_indexes
        where schemaname = 'public'
          and tablename = 'products'
          and indexname = 'idx_products_lower_name'
    ) then
        execute 'create index idx_products_lower_name on public.products (lower(name));';
    end if;
end$$;

-- Unique index on sku is already enforced by column constraint, but keep an explicit index name if desired:
do $$
begin
    if not exists (
        select 1 from pg_indexes
        where schemaname = 'public'
          and tablename = 'products'
          and indexname = 'ux_products_sku'
    ) then
        execute 'create unique index ux_products_sku on public.products (sku);';
    end if;
end$$;

-- Trigger function to update updated_at on row updates
create or replace function public.set_updated_at_timestamp()
returns trigger
language plpgsql
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

-- Trigger to update updated_at before updates
do $$
begin
    if not exists (
        select 1
        from pg_trigger
        where tgname = 'trg_products_set_updated_at'
    ) then
        execute '
            create trigger trg_products_set_updated_at
            before update on public.products
            for each row
            execute function public.set_updated_at_timestamp()
        ';
    end if;
end$$;

-- Optional: Trigram index for fuzzy search on product names (improves ILIKE %term% performance)
-- Requires pg_trgm extension (enabled above). Uncomment to use.
-- create index if not exists idx_products_name_trgm on public.products using gin (name gin_trgm_ops);

-- Notes:
-- - image_url can be a public URL to Supabase Storage (or signed URL if private bucket).
-- - image_path stores the storage object path (e.g., products/abc123.png) for server-side operations.
-- - For stricter SKU format validation, consider a check constraint or do validation in your backend layer.
