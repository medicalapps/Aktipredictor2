Variables = {
    "databuilder":
    {
        "SectorBranch": {
            "Energi": {
                "ID": 3,
                "Brancher": {
                    "OljaGasBorrning": 1,
                    "OljaGasExploatering": 2,
                    "OljaGasTransport": 3,
                    "OljaGasForsealjning": 4,
                    "OljaGasService": 5,
                    "BreansleKol": 6,
                    "BreansleUran": 7
                }
            },
            "Kraftforsorjning": {
                "ID": 10,
                "Brancher": {
                    "Elforsorjning": 8,
                    "Gasforsorjning": 9,
                    "Vattenforsorjning": 10,
                    "Fornybarenergi": 11,
                    "Vindkraft": 12,
                    "Solkraft": 13,
                    "Bioenergi": 14
                }
            },
            "Material": {
                "ID": 7,
                "Brancher": {
                    "Kemikalier": 15,
                    "GruvProspektDrift": 16,
                    "GruvIndustrimetaller": 17,
                    "GruvGuldSilver": 18,
                    "Gruveadelstenar": 19,
                    "GruvService": 20,
                    "Skogsbolag": 21,
                    "Forpackning": 22
                }
            },
            "Dagligvaror": {
                "ID": 2,
                "Brancher": {
                    "Drycker": 58,
                    "Jordbruk": 59,
                    "Fiskodling": 60,
                    "Tobak": 61,
                    "Livsmedel": 62,
                    "Hygienprodukter": 63,
                    "Healsoprodukter": 64,
                    "Apotek": 65,
                    "Livsmedelsbutiker": 66
                }
            },
            "Seallankopsvaror": {
                "ID": 8,
                "Brancher": {
                    "KleaderSkor": 43,
                    "Accessoarer": 44,
                    "Hemelektronik": 45,
                    "MoblerInredning": 46,
                    "FritidSport": 47,
                    "BilMotor": 48,
                    "Konsumentservice": 49,
                    "Detaljhandel": 50,
                    "HotellCamping": 51,
                    "RestaurangCafe": 52,
                    "ResorNojen": 53,
                    "BettingCasino": 54,
                    "GamingSpel": 55,
                    "Marknadsforing": 56,
                    "MediaPublicering": 57
                }
            },
            "Industri": {
                "ID": 5,
                "Brancher": {
                    "Industrimaskiner": 23,
                    "Industrikomponenter": 24,
                    "ElektroniskaKomponenter": 25,
                    "MilitearForsvar": 26,
                    "Energiatervinning": 27,
                    "ByggnationInfrastruktur": 28,
                    "Bostadsbyggnation": 29,
                    "InstallationVVS": 30,
                    "Byggmaterial": 31,
                    "Bygginredning": 32,
                    "Bemanning": 33,
                    "Affearskonsulter": 34,
                    "Seakerhet": 35,
                    "Utbildning": 36,
                    "StodtjeansterService": 37,
                    "MeatningAnalys": 38,
                    "InformationData": 39,
                    "Flygtransport": 40,
                    "SjofartRederi": 41,
                    "TagLastbilstransport": 42
                }
            },
            "Healsovard": {
                "ID": 4,
                "Brancher": {
                    "Leakemedel": 77,
                    "Biotech": 78,
                    "MedicinskUtrustning": 79,
                    "HealsovardHjealpmedel": 80,
                    "SjukhusVardhem": 81
                }
            },
            "FinansFastighet": {
                "ID": 1,
                "Brancher": {
                    "Banker": 68,
                    "Nischbanker": 69,
                    "KreditFinansiering": 70,
                    "Kapitalforvaltning": 71,
                    "Fondforvaltning": 72,
                    "Investmentbolag": 73,
                    "Forseakring": 74,
                    "Fastighetsbolag": 75,
                    "FastighetREIT": 76
                }
            },
            "Informationsteknik": {
                "ID": 6,
                "Brancher": {
                    "ElektronikTillverkning": 82,
                    "DatorerHardvara": 83,
                    "ElektroniskUtrustning": 84,
                    "Biometri": 85,
                    "Kommunikation": 86,
                    "RymdSatellitteknik": 87,
                    "SeakerhetBevakning": 88,
                    "ITKonsulter": 89,
                    "AffearsITSystem": 90,
                    "Internettjeanster": 91,
                    "BetalningEhandel": 92
                }
            },
            "Telekommunikation": {
                "ID": 9,
                "Brancher": {
                    "BredbandTelefoni": 93,
                    "Telekomtjeanster": 94
                }
            }
        }
    },

    "training":
    {
        "PredictionPart": 0.01,
        "currentbranch": "16",
        "currentsector": "7",
        "lookToTheFuture": 1,
        "lr": 0.0002,
        "stockTrainingTime": 60,
        "trainingDataWindow": 30,
        "weightlimit_high": 0.1,
        "weightlimit_low": -0.1,
        "bias_high": 0.1,
        "bias_low": -0.1,
        "UseMockData": False,

    },

}
