# Supabase Storage Setup (Products Bucket)

This guide sets up a Storage bucket for product images used by the Product Inventory Manager.

## 1) Create the "products" bucket

For MVP we will use a public bucket for simple direct image access from the frontend.

1. Go to Supabase Dashboard → Storage → Create new bucket
2. Name: `products`
3. Public: Enabled (checked)
4. Create

Alternatively via SQL:

```sql
-- Create a public bucket named 'products'
insert into storage.buckets (id, name, public)
values ('products', 'products', true)
on conflict (id) do nothing;
```

## 2) Storage Policies

Even if the bucket is public, we recommend:
- Allow read for anon (public content).
- Restrict writes to service role or via verified backend logic.

Example policies (run in the SQL editor):

```sql
-- Allow ANYONE to read objects in the public bucket
create policy "Public read for products"
on storage.objects for select
to anon
using (bucket_id = 'products');

-- Allow service role to perform all operations
-- Note: service role bypasses RLS, but we include explicit policy examples
create policy "Service role full access"
on storage.objects for all
to service_role
using (bucket_id = 'products')
with check (bucket_id = 'products');
```

If you plan to allow authenticated users to upload, you would add additional policies for `authenticated` role and limit paths, e.g., to `auth.uid()` folders. For this MVP, uploads should be performed by the backend using the `SUPABASE_SERVICE_ROLE_KEY`.

## 3) Object Path Convention

- Store images under `products/` prefix, e.g., `products/<uuid>.png`.
- Save the object path to the `image_path` column in the `products` table.
- Save the final public URL (or signed URL) into `image_url` for easy retrieval by clients.

## 4) Switching to a Private Bucket (Recommended for Production)

To enhance security in production:

1. Make the bucket private:
   - Dashboard → Storage → Edit bucket → uncheck Public (or recreate the bucket as private)

2. Update/Adjust Policies (private bucket typically does not allow anon select):
   - Remove the public read policy above or do not create it.
   - Keep service_role write access via backend.

3. Serve Images via Signed URLs:
   - The backend generates signed URLs using Supabase client and returns them to the frontend.
   - Signed URLs should use an expiry (e.g., `URL_SIGN_EXPIRY_SECONDS` from `.env`).

Example SQL (private bucket + no anon policy):

```sql
-- Private bucket creation
insert into storage.buckets (id, name, public)
values ('products', 'products', false)
on conflict (id) do nothing;

-- Service role policy (explicit)
create policy "Service role full access"
on storage.objects for all
to service_role
using (bucket_id = 'products')
with check (bucket_id = 'products');
```

4) Client Behavior:
- Frontend requests image URL from backend.
- Backend generates a signed URL (valid for configured seconds) and responds.
- Frontend uses the signed URL to display the image.

## 5) CORS

Ensure your backend allows requests from your frontend origin (see `.env.example` `CORS_ORIGINS`).

## 6) Cleanup and Lifecycle

- On product delete: remove the associated object by `image_path` from the `products` bucket.
- On product update with new image: upload new object, update `image_url`/`image_path`, optionally delete the old object.

## References

- Supabase Storage Docs: https://supabase.com/docs/guides/storage
- Supabase RLS for Storage: https://supabase.com/docs/guides/storage#policies
