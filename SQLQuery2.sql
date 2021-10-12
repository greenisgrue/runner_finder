DELETE FROM dbo.RaceData;

BULK INSERT dbo.RaceData
   FROM 'C:\Users\Simon Wahlstr�m\Documents\Projects\DataScraping\master_files\race_data.csv'  
   WITH   
      (  
	     FIRSTROW = 2,
		 CODEPAGE = '65001',
		 DATAFILETYPE = 'widechar',
         FIELDTERMINATOR =',',  
         ROWTERMINATOR ='\n'  
      );
GO