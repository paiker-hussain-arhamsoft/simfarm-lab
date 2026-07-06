import { Router, type IRouter } from "express";
import healthRouter from "./health";
import activityRouter from "./activity";
import adminRouter from "./admin";
import agentsRouter from "./agents";
import intelligenceRouter from "./intelligence";
import mediaRouter from "./media";
import videoRouter from "./video";
import cyberRouter from "./cyber";
import personaRouter from "./persona";
import simRouter from "./sim";
import proxyRouter from "./proxy";
import ivrRouter from "./ivr";
import contentRouter from "./content";
import stealthRouter from "./stealth";
import memoryRouter from "./memory";
import simfarmRouter from "./simfarm";

const router: IRouter = Router();

router.use(healthRouter);
router.use(activityRouter);
router.use(adminRouter);
router.use(agentsRouter);
router.use(intelligenceRouter);
router.use(mediaRouter);
router.use(videoRouter);
router.use(cyberRouter);
router.use(personaRouter);
router.use(simRouter);
router.use(proxyRouter);
router.use(ivrRouter);
router.use(contentRouter);
router.use(stealthRouter);
router.use(memoryRouter);
router.use(simfarmRouter);

export default router;
