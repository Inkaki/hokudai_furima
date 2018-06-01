# Generated by Django 2.0.3 on 2018-03-28 16:33

from django.db import migrations, models
import django.db.models.deletion
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_product_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', versatileimagefield.fields.VersatileImageField(upload_to='products/images/', verbose_name='Image')),
                ('optional_image1', versatileimagefield.fields.VersatileImageField(blank=True, upload_to='products/images/', verbose_name='Optional Image1')),
                ('optional_image2', versatileimagefield.fields.VersatileImageField(blank=True, upload_to='products/images/', verbose_name='Optional Image2')),
                ('optional_image3', versatileimagefield.fields.VersatileImageField(blank=True, upload_to='products/images/', verbose_name='Optional Image3')),
                ('alt', models.CharField(blank=True, max_length=128)),
                ('order', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'ordering': ('order',),
            },
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='product.ProductImage'),
        ),
    ]