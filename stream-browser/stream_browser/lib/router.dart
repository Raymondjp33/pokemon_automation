import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'pages/control_panel/control_panel_state.dart';
import 'pages/one_switch/one_switch_state.dart';
import 'pages/sandbox/sandbox_state.dart';
import 'pages/three_switch/three_switch_state.dart';
import 'pages/two_switch/two_switch_state.dart';
import 'pages/showcased_switch/showcased_switch_state.dart';

class NavKeyService {
  static GlobalKey<NavigatorState> globalNavigationKey =
      GlobalKey<NavigatorState>();
}

enum ERoute {
  controlPanel(name: 'controlPanel', path: '/'),
  oneSwitch(name: 'oneSwitch', path: '/oneSwitch'),
  twoSwitch(name: 'twoSwitch', path: '/twoSwitch'),
  threeSwitch(name: 'threeSwitch', path: '/threeSwitch'),
  showcasedSwitch(name: 'showcasedSwitch', path: '/showcasedSwitch'),
  sandbox(name: 'sandbox', path: '/sandbox');

  final String name;
  final String path;
  const ERoute({required this.name, required this.path});
}

final GoRouter router = GoRouter(
  navigatorKey: NavKeyService.globalNavigationKey,
  initialLocation: ERoute.twoSwitch.path,
  restorationScopeId: 'router',
  routes: <RouteBase>[
    GoRoute(
      name: ERoute.controlPanel.name,
      path: ERoute.controlPanel.path,
      builder: (BuildContext context, GoRouterState state) {
        return ControlPanel();
      },
    ),
    GoRoute(
      name: ERoute.oneSwitch.name,
      path: ERoute.oneSwitch.path,
      builder: (BuildContext context, GoRouterState state) {
        return OneSwitch();
      },
    ),
    GoRoute(
      name: ERoute.twoSwitch.name,
      path: ERoute.twoSwitch.path,
      builder: (BuildContext context, GoRouterState state) {
        return TwoSwitch();
      },
    ),
    GoRoute(
      name: ERoute.threeSwitch.name,
      path: ERoute.threeSwitch.path,
      builder: (BuildContext context, GoRouterState state) {
        return ThreeSwitch();
      },
    ),
    GoRoute(
      name: ERoute.showcasedSwitch.name,
      path: ERoute.showcasedSwitch.path,
      builder: (BuildContext context, GoRouterState state) {
        return ShowcasedSwitch();
      },
    ),
    GoRoute(
      name: ERoute.sandbox.name,
      path: ERoute.sandbox.path,
      builder: (BuildContext context, GoRouterState state) {
        return Sandbox();
      },
    ),
  ],
);
