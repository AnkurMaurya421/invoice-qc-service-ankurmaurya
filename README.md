# invoice-qc-service-ankurmaurya
This is an assignment for the position of SDE Intern at DeepLogic AI.



# Schema and Validation Design
Given Sample PDFs for data extraction are in German language.
So we will use field mapping from german to english , the logic remains same for any language by using mapping.

After reviewing the sample pdfs structure and their fields , list of fields selected 
for schema are given below

### Invoice Level Fields

1.  Invoice Id              -> Generate this for each invoice to identify the object.(Unique internal identifier)
2.  Invoice Number          -> Order / invoice number extracted from header. (Mandatory Field)
3.  Reference Number        -> Invoice number reference to customer or project
4.  Invoice Date            -> Date of invoice  (Mandatory Field)
5.  Seller Name             -> Name of supplier (Mandatory Field)
6.  Buyer Name              -> Name of Customer (Mandatory Field)         
7.  Customer Number         -> Customer Number in Sellers System 
8.  End Customer Number     -> Not mandatory 
9.  Net Total               -> Mandatory
10. Tax(Percentage)         -> Not Mandatory
11. Gross Total             -> Mandatory =(total value including tax if tax is present)

### Line Items Fields


1.  Description             -> 
2.  quantity                -> 
3.  Price per unit          -> 
4.  line total              ->  
5.  Currency                -> 


### Validation Rules

#### Completeness Rules:
##### Mandatory Fields Check
invoice_numberinvoice_date
->seller_name
->buyer_name
->net_total
->gross_total
->line_items (at least one)
