import React, { Fragment, useEffect, useState } from "react";
//import Typography from '@mui/material/Typography';

import Modal from "@mui/joy/Modal";
import ModalDialog from "@mui/joy/ModalDialog";

import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Container from "@mui/material/Container";
import Card from "@mui/joy/Card";
import CardContent from "@mui/joy/CardContent";
import CircularProgressJoy from "@mui/joy/CircularProgress";
import SvgIcon from "@mui/joy/SvgIcon";
//import Link from '@mui/joy/Link';
import { Link, useNavigate } from "react-router";

import CardActions from "@mui/joy/CardActions";
import Button from "@mui/joy/Button";
import Typography from "@mui/joy/Typography";
import Table from "@mui/joy/Table";

const DASHBOARD_API_ENDPOINT = "http://localhost:5000/api/v1/dashboards";
const DATASET_API_ENDPOINT = "http://localhost:5000/api/v1/datasets"

export default function HomePage() {
  let navigate = useNavigate();

  // React hooks

  const [dashboards, setDashboards] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const [sliceConfigMap, setSliceConfigMap] = useState([] as any);

  const getDashboards = async () => {
    setIsLoading(true);
    const dashboardGetResponse = await fetch(DASHBOARD_API_ENDPOINT, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });

    const dashboardData = await dashboardGetResponse.json();
    //console.info(dashboardData)

    let dashboardListing: any = [];
    dashboardData.forEach(function (item: any) {
      let newObject: any = {
        id: item.id,
        dashboard_title: item.dashboard_title,
        changed_on_delta_humanized: item.changed_on_delta_humanized,
        status: item.status,
      };
      dashboardListing.push(newObject);
    });
    //console.info(dashboardListing)

    setDashboards(dashboardListing);
    setIsLoading(false);

    return;
  };

  const getDatasets = async () => {
  
  const datasetGetResponse = await fetch(DATASET_API_ENDPOINT, {
    method: 'GET',
    headers: {
      'Accept': 'application/json'
    }
  })
  const datasetData = await datasetGetResponse.json();
  //console.info(datasetData)
  let datasetListing: any = [];
    datasetData.forEach(function (item: any) {
      let newObject: any = {
        dataset_id: item.id,
        dataset: item.table_name,
        datasource_type: item.datasource_type,
        modified: item.changed_on_delta_humanized,
        database_id: item.database.id,
        database_name: item.database.database_name,
        schema: item.schema,
        explore_url: item.explore_url
      };
      datasetListing.push(newObject);
    });
  //console.info(datasetListing)

  //if (!datasetListing) {
    //console.warn("Dataset listing missing from response. Check if the Superset API has been changed.");   
  //}
  //setDatasetList(datasetListing)

return datasetGetResponse;
}

  const onLoadDashboardDetails = async (
    dashboardId: number,
    dashboard_title: string
  ) => {
    navigate(`dashboard/${dashboardId}`, {
      state: {
        dashboardId,
        dashboard_title,
      },
    });
  };

  

  useEffect(() => {
    getDashboards();
    //getDatasets();
  }, [DASHBOARD_API_ENDPOINT, DATASET_API_ENDPOINT]);

  return (
    <Fragment>
      {isLoading ? (
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: "absolute",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <CircularProgress color="secondary" size="25px" />
        </Box>
      ) : null}

      <Box
        sx={{
          width: "100%",
          maxWidth: 1000,
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))",
          gap: 2,
          paddingBottom: 3,
        }}
      >
        {dashboards?.map(
          ({
            id,
            dashboard_title,
            status,
            changed_on_delta_humanized,
          }: any) => (
            <div key={id}>
              <Card variant="outlined">
                <CardContent>
                  <Link
                    to="#"
                    style={{ textDecoration: "none" }}
                    state={{ dashboardTitle: dashboard_title }}
                    onClick={() => onLoadDashboardDetails(id, dashboard_title)}
                  >
                    <Typography
                      level="title-md"
                      textColor="inherit"
                      sx={{
                        fontWeight: "normal",
                        color: "#004687",
                      }}
                    >
                      {dashboard_title}
                    </Typography>
                  </Link>
                  <Typography
                    textColor="inherit"
                    sx={{ textTransform: "capitalize" }}
                  >
                    {status}
                  </Typography>
                  <Typography level="body-xs">
                    {changed_on_delta_humanized}
                  </Typography>
                </CardContent>
              </Card>
            </div>
          )
        )}
      </Box>
    </Fragment>
  );
}
