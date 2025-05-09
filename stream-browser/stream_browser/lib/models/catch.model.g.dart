// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'catch.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CatchModel _$CatchModelFromJson(Map<String, dynamic> json) => CatchModel(
      encounters: (json['encounters'] as num?)?.toInt(),
      caughtTimestamp: json['caught_timestamp'] as num?,
      startedHuntTimestamp: json['started_hunt_timestamp'] as num?,
    );

Map<String, dynamic> _$CatchModelToJson(CatchModel instance) =>
    <String, dynamic>{
      'encounters': instance.encounters,
      'caught_timestamp': instance.caughtTimestamp,
      'started_hunt_timestamp': instance.startedHuntTimestamp,
    };
